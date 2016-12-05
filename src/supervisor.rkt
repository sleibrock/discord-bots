#lang racket/base

(require racket/system racket/list)
(provide
 bots
 total-bots
 subproc
 subproc-kill
 start-bot
 reviver
 main
 )

;; Define bots here - file to execute, keys, colors for logging
(define bots
  (vector
    (list "python"     "src/dumb-bot.py")
    (list "python"    "src/graph-bot.py")
    (list "python"   "src/hacker-bot.py")
    (list "python"  "src/janitor-bot.py")
    (list "node"    "src/FishFactBot.js")
    ))
(define total-bots (vector-length bots)) ; store how many have been set up

;; Creates a new function which prints out a message with a name attached
(define (set-logger t-name color)
  (λ (str)
    (define cd (seconds->date (current-seconds))) 
    (displayln
     (apply (λ (x y z) (format "[\033[38;5;~am~a\033[0m @ ~a:~a:~a] ~a" color t-name x y z str))
            (map (λ (i) (if (< i 10) (format "0~a" i) (format "~a" i)))
                 (list (date-hour cd) (date-minute cd) (date-second cd)))))))

(define logger (set-logger "supervisor  " 9))

;; a quick wrapper function for subprocess 
(define (subproc p a)
  (parameterize ([current-subprocess-custodian-mode 'kill])
    (apply
     subprocess
     (append (list (current-output-port) #f 'stdout (find-executable-path p)) a))))

;; A one-arg subprocess-kill wrapper
(define (subproc-kill subp)
  (subprocess-kill subp #t))

;; Create a new subprocess and return it
(define (start-bot bot-id)
  (define-values (interp code) (apply values (vector-ref bots bot-id)))
  (define-values (a b c d)
    (subproc interp (list code)))
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
  (define (loop)
    (for-each revive (range total-bots))
    (sleep 300) ; number of seconds the gravekeeper should sleep
    (loop))
  (loop))

; end
