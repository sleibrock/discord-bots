#lang racket/base

(require racket/system racket/file racket/cmdline)
(require json)

;; Used to color the supervisor's message output and color
(define fstring "[\033[38;5;~am~a\033[0m @ ~a:~a:~a] ~a")

;; define a range function without using racket/list
(define (span x)
  (define (inner x lst)
    (if (< x 0)
        lst
        (inner (sub1 x) (cons x lst))))
  (cond
    [(< x 1) '()]
    [else (inner (sub1 x) '())]))

;; Creates a new function which prints out a message with a name attached
(define (set-logger t-name color)
  (λ (str)
    (define cd (seconds->date (current-seconds))) 
    (displayln
     (apply (λ (x y z) (format fstring color t-name x y z str))
            (map (λ (i) (if (< i 10) (format "0~a" i) (format "~a" i)))
                 (list (date-hour cd) (date-minute cd) (date-second cd)))))))

(define logger (set-logger "supervisor  " 9))

;; Create a boty factory which uses a source as a reference point (rather, blueprints)
(define (bot-factory bot-source)
  (λ (bot-id)
    (define bot (vector-ref bot-source bot-id))
    (define-values (a b c d)
      (parameterize ([current-subprocess-custodian-mode 'kill])
        (subprocess
         (current-output-port)
         #f
         'stdout
         (find-executable-path (symbol->string (car bot)))
         (cdr bot))))
    (logger (format "Initialized Bot ~a on PID ~a" bot-id (subprocess-pid a)))
    a))
  
;; Revive a subprocess as required
(define (reviver threads res-func)
  (λ (bot-id)
    (define subp (vector-ref threads bot-id))
    (when (not (eqv? 'running (subprocess-status subp)))
      (subprocess-kill subp #t)
      (vector-set! threads bot-id (res-func bot-id)))))

;; The main program to run with the command-line
(define (supervisor cfg-file)
  (define jdata (read-json (open-input-file cfg-file)))
  (define hard-restart (hash-ref jdata 'hard_restarts #t))
  (define sleep-count  (hash-ref jdata 'sleep_count 12))
  (define sleep-time   (hash-ref jdata 'sleep_time 300))
  (define init-sleep   (hash-ref jdata 'init_sleep 30))
  (define bots         (list->vector (map (compose car hash->list) (hash-ref jdata 'bots))))
  (define total-bots   (vector-length bots)) ; store how many have been set up
  (define start-bot (bot-factory bots))

  (define (cust-loop)
    (logger "Starting Custodian")
    (define cust (make-custodian))
    (parameterize ([current-custodian cust])
      (define threads (build-vector total-bots start-bot))
      (define revive (reviver threads start-bot))
      (logger "Threads initialized")
      (sleep init-sleep)
      (define (loop x)
        (unless (= x sleep-count)
          (logger "Checking on bots")
          (for-each revive (span total-bots))
          (sleep sleep-time)
          (loop (add1 x))))
      (loop 0))
    (when hard-restart
      (logger "Shutting down Custodian")
      (custodian-shutdown-all cust)
      (sleep 30))
    (cust-loop))
  (cust-loop))

(module+ main
  (command-line
   #:program "supervisor"
   #:args (config-file)
   (supervisor config-file)))

; end
