#lang racket/base

(require racket/string racket/system racket/list)

;; Program to hypervise bot threads
;; Step 1: create a vector of Bot threads
;; Step 2: check whether a thread has been finished or not
;; Step 3: if a thread is dead, re-activate the thread with the original bot
;; Step 4: sleep for a little bit before re-checking threads
;; Step 5: every 72 hours, restart each bot thread

;; Define bots here - file to execute and their keys
(define bots
  (vector
    (list "python" "bots/dumb-bot.py"    "dumb-bot.key")
    (list "python" "bots/remind-bot.py"  "remind-bot.key")
    (list "python" "bots/graph-bot.py"   "graph-bot.key")
    (list "python" "bots/janitor-bot.py" "janitor-bot.key")
    ))

;; Functions ################################################################
;; Convert a bot struct into an executable string
(define (bot->command bot) (string-join bot " "))

;; Turn a bot into a thread
(define (start-bot bot-id)
  (thread
   (λ ()
     (displayln (format "Starting bot ~a" bot-id))
     (system (bot->command (vector-ref bots bot-id)))
     (displayln (format "Bot ID ~a ended unexpectedly" bot-id)))))

;; The necromancer function to create new threads from dead matter
(define (re-animate id)
  (displayln (format "Checking thread ~a" id))
  (when (thread-dead? (vector-ref threads id))
    (displayln (format "Bringing thread ~a back to life" id))
    (vector-set! threads id (start-bot id))))

(define (kill-bot id)
  (displayln (format "Assassinating thread ~a" id))
  (kill-thread (vector-ref threads id)))

;; Variables ###############################################################
;; Total number of bots we have to manage
(define total-bots (vector-length bots))

;; The bot threads to maintain
(define threads
  (build-vector total-bots start-bot))

;; Thread assassin to restart threads every 72 hours
;; Assurance that each thread will always be running
(define assassin
  (thread
   (λ ()
     (displayln "Assassin thread started")
     (define (loop)
       (sleep 259200)
       (displayln "Beginning assassination")
       (for ([x (in-range total-bots)])
         (kill-bot x))
       (displayln "Assassin going to sleep")
       (loop))
     (loop))))

;; Main loop and re-activation thread
(define main-t
  (thread
   (λ ()
     (sleep 30) ; wait for bots to start before looping
     (define (loop)
       (sleep 300) ; number of seconds the gravekeeper should sleep
       (displayln "Beginning Gravekeeper sweep...")
       (for ([x (in-range total-bots)])
         (re-animate x))
       (displayln "Sleeping Gravekeeper...")
       (loop))
     (loop))))

; basically an infinite loop/wait
(thread-wait main-t)

