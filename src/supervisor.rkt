#lang racket/base

(require racket/system)
(provide bots total-bots main syscall)

;; Shortcut to do syscalls with multiple arguments
;; syscall :: (Listof String) -> Boolean
(define (syscall cmds)
  (parameterize ([current-subprocess-custodian-mode 'kill])
    (apply system* (append (list (find-executable-path (car cmds))) (cdr cmds)))))

;; bots :: (Vectorof (Listof String))
(define bots
  (vector
    '("python"    "src/dumb-bot.py")
    '("python"   "src/graph-bot.py")
    '("python"  "src/hacker-bot.py")
    '("python" "src/janitor-bot.py")
    '("node"   "src/FishFactBot.js")))
(define total-bots (vector-length bots))

;; Creates a new function which prints out a message with a name attached
;; set-logger :: String -> String -> String -> Void
(define (set-logger t-name color)
  (λ (str)
    (define cd (seconds->date (current-seconds))) 
    (displayln
     (apply (λ (x y z) (format "[\033[38;5;~am~a\033[0m @ ~a:~a:~a] ~a" color t-name x y z str))
            (map (λ (i) (if (< i 10) (format "0~a" i) (format "~a" i)))
                 (list (date-hour cd) (date-minute cd) (date-second cd)))))))
(define logger (set-logger "supervisor  " 1))

;; Create a function which will yield new threads that send data to a parent thread
;; bot-factory :: Thread -> Nonnegative-Integer -> Thread
(define (bot-factory parent-thread)
  (λ (bot-id)
    (thread
     (λ ()
       (logger (format "Starting Bot ~a" bot-id))
       (syscall (vector-ref bots bot-id)) 
       (thread-send parent-thread bot-id)))))

;; Create a thread reviving function corresponding to a vector of threads
;; reviver :: (Vectorof Threads) -> (-> Nonnegative-Integer Thread) -> Void
(define (reviver threads bot-func)
  (λ (bot-id)
    (vector-set! threads bot-id (bot-func bot-id)))) 

;; Gravekeeper main function to keep the subprocesses running
;; main :: Void
(define (main)
  (define start-bot (bot-factory (current-thread)))
  (define threads (build-vector total-bots start-bot))
  (define revive (reviver threads start-bot))
  (sleep 30) ; wait for bots to start before looping
  (define (loop)
    (revive (thread-receive))
    (loop))
  (loop))

; end
