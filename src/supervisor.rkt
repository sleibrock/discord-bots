#lang racket/base

(require racket/system racket/list)
(provide
 bots
 total-bots
 start-bot
 reviver
 main
 )

;; Define bots here - file to execute, keys, colors for logging
(define bots
  (vector
    (list "python"     "bots/dota-bot.py")
    (list "python"     "bots/dumb-bot.py")
    (list "python"    "bots/graph-bot.py")
    (list "python"   "bots/hacker-bot.py")
    (list "python"  "bots/janitor-bot.py")
    (list "node"    "bots/FishFactBot.js")
    ))
(define total-bots (vector-length bots)) ; store how many have been set up
(define fstring "[\033[38;5;~am~a\033[0m @ ~a:~a:~a] ~a")

;; Creates a new function which prints out a message with a name attached
(define (set-logger t-name color)
  (λ (str)
    (define cd (seconds->date (current-seconds))) 
    (displayln
     (apply (λ (x y z) (format fstring color t-name x y z str))
            (map (λ (i) (if (< i 10) (format "0~a" i) (format "~a" i)))
                 (list (date-hour cd) (date-minute cd) (date-second cd)))))))

(define logger (set-logger "supervisor  " 9))

;; Create a new subprocess and return it
(define (start-bot bot-id)
  (define-values (interp code) (apply values (vector-ref bots bot-id)))
  (define-values (a b c d)
    (parameterize ([current-subprocess-custodian-mode 'kill])
      (subprocess (current-output-port) #f 'stdout (find-executable-path interp) code)))
  (logger (format "Initialized Bot ~a on PID ~a" bot-id (subprocess-pid a)))
  a)

;; Revive a subprocess as required
(define (reviver threads)
  (λ (bot-id)
    (define subp (vector-ref threads bot-id))
    (when (not (eqv? 'running (subprocess-status subp)))
      (subprocess-kill subp #t)
      (vector-set! threads bot-id (start-bot bot-id)))))

;; Gravekeeper main function to keep the subprocesses running
(define (main)
  (define threads (build-vector total-bots start-bot))
  (define revive (reviver threads))
  (logger "Gravekeeper thread initialized")
  (sleep 30) ; wait for bots to start before looping
  (define (loop x)
    (when (= x 12)
      (for-each
       (λ (id)
         (subprocess-kill (vector-ref threads id) #t)
         (sleep 1)
         (vector-set! threads id (start-bot id)))
       (range total-bots))
      (loop 0))
    (for-each revive (range total-bots))
    (sleep 300) ; number of seconds the gravekeeper should sleep
    (loop (add1 x)))
  (loop 0))

; end
