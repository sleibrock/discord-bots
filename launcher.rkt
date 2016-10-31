#lang racket/base

(require racket/string racket/system racket/list)

;; Program to hypervise bot threads
;; Step 1: create a vector of Bot threads
;; Step 2: check whether a thread has been finished or not
;; Step 3: if a thread is dead, re-activate the thread with the original bot
;; Step 4: sleep for a little bit before re-checking threads
;; Step 5: every 72 hours, restart each bot thread (if they make it that far)

;; Define bots here - file to execute, keys, colors for logging
(define bots
  (vector
    (list "python"    "bots/dumb-bot.py"    "dumb-bot.key")
    (list "python"  "bots/remind-bot.py"  "remind-bot.key")
    (list "python"   "bots/graph-bot.py"   "graph-bot.key")
    (list "python" "bots/janitor-bot.py" "janitor-bot.key")
    ))
(define total-bots (vector-length bots))

;; Logger function to print statements to terminal
(define (logger str)
  (define cd (seconds->date (current-seconds))) 
  (displayln
   (apply (λ (x y z) (format "[\033[38;5;9msupervisor\033[0m  @ ~a:~a:~a] ~a" x y z str))
          (map (λ (i) (if (< i 10) (format "0~a" i) (format "~a" i)))
               (list (date-hour cd) (date-minute cd) (date-second cd))))))

;; Convert a bot struct into an executable string
(define (bot->command bot) (string-join bot " "))

;; Turn a bot into a thread
(define (start-bot bot-id)
  (thread
   (λ ()
     (logger (format "Starting bot ~a" bot-id))
     (system (bot->command (vector-ref bots bot-id)))
     (logger (format "Bot ID ~a ended unexpectedly" bot-id)))))

;; The necromancer function to create new threads from dead matter
(define (re-animate id)
  (logger (format "Checking thread ~a" id))
  (when (thread-dead? (vector-ref threads id))
    (logger (format "Bringing thread ~a back to life" id))
    (vector-set! threads id (start-bot id))))

;; Function to kill a target thread via it's ID
(define (kill-bot id)
  (logger (format "Assassinating thread ~a" id))
  (kill-thread (vector-ref threads id)))

;; The bot threads to maintain
(define threads (build-vector total-bots start-bot))

;; Thread assassin to restart threads every 24 hours
;; Assurance that each thread will always be running
;; Also frees up leftover memory from programs running for a long time
(define assassin
  (thread
   (λ ()
     (logger "Assassin thread started")
     (define (loop)
       (sleep 86400)
       (logger "Beginning assassination")
       (for ([x (in-range total-bots)])
         (kill-bot x))
       (logger "Assassin going to sleep")
       (loop))
     (loop))))

;; Main loop and re-activation thread
(define main-t
  (thread
   (λ ()
     (sleep 30) ; wait for bots to start before looping
     (define (loop)
       (sleep 300) ; number of seconds the gravekeeper should sleep
       (logger "Beginning Gravekeeper sweep...")
       (for ([x (in-range total-bots)])
         (re-animate x))
       (logger "Sleeping Gravekeeper...")
       (loop))
     (loop))))

; basically an infinite loop/wait
(thread-wait main-t)

