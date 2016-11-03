#lang racket/base

(require racket/string racket/system racket/list)

; Step 1: create a vector of Bot threads
; Step 2: check whether a thread has been finished or not
; Step 3: if a thread is dead, re-activate the thread with the original bot
; Step 4: sleep for a little bit before re-checking threads
; Step 5: every 72 hours, restart each bot thread (if they make it that far)

; Define bots here - file to execute, keys, colors for logging
(define bots
  (vector
    (list "python"    "bots/dumb-bot.py"    "dumb-bot.key")
    (list "python"  "bots/remind-bot.py"  "remind-bot.key")
    (list "python"   "bots/graph-bot.py"   "graph-bot.key")
    (list "python" "bots/janitor-bot.py" "janitor-bot.key")
    ))
(define total-bots (vector-length bots)) ; store how many have been set up
(define cust (make-custodian))           ; our custodian to use for all threads

; Creates a new function which prints out a message with a name attached
; Used to create the gravekeeper's logger, the assassin's logger, etc
(define (set-logger t-name color)
  (λ (str)
    (define cd (seconds->date (current-seconds))) 
    (displayln
     (apply (λ (x y z) (format "[\033[38;5;~am~a\033[0m  @ ~a:~a:~a] ~a" color t-name x y z str))
            (map (λ (i) (if (< i 10) (format "0~a" i) (format "~a" i)))
                 (list (date-hour cd) (date-minute cd) (date-second cd)))))))

(define gk-log (set-logger "gravekeeper" 9))
(define as-log (set-logger "assassin   " 3))

; Get all things managed by our custodian
(define (get-all-resources [type (λ (x) #t)])
  (filter type (custodian-managed-list cust (current-custodian))))

; A one-arg subprocess-kill wrapper
(define (subproc-kill subp)
  (subprocess-kill subp #t))

; Multiple-type kill function to kill all objects in the custodian
(define (kill-object thing)
  (cond [(thread? thing) (kill-thread thing)]
        [(subprocess? thing) (subproc-kill thing)]))

; Convert a bot struct into an executable string
(define (bot->command bot) (string-join bot " "))

; Turn a bot into a thread
; Subprocess calls are different from Racket threads, and by default
; Subprocesses aren't placed into a custodian (why though?)
; Using the `current-subprocess-custodian-mode` we can place them into the
; Custodian management pool, and we can manage them from there
(define (start-bot bot-id)
  (parameterize ([current-custodian cust] [current-subprocess-custodian-mode 'kill])
    (thread
     (λ ()
       (gk-log (format "Starting bot ~a" bot-id))
       (system (bot->command (vector-ref bots bot-id)))
       (gk-log (format "Bot ID ~a ended unexpectedly" bot-id))))))

; Start all bots (we don't have to store it; they are placed under the custodian)
(define (start-all-bots)
  (build-vector total-bots start-bot))

; End all bots by killing each thread/subproc under the Custodian's management
(define (end-all-bots)
  (for-each kill-object (get-all-resources)))

; Thread assassin to restart threads every 24 hours
; Assurance that each thread will always be running
; Also frees up leftover memory from programs running for a long time
; Does not revive threads once they're killed; that's for the gravekeeper
(define assassin
  (thread
   (λ ()
     (as-log "Hideout set-up, awaiting contracts...")
     (define (loop)
       (sleep 86400) ; a day is equal to 24*60*60
       (as-log "Putting targets to sleep")
       (end-all-bots)
       (loop))
     (loop))))

; Gravekeeper thread
; When one bot goes down, shut them all down and restore them manually
; Until we find a better way to store PIDs and check if those are alive,
; we'll have to do with the "if one goes down, all go down" policy
(define main-t
  (thread
   (λ ()
     (start-all-bots)
     (gk-log "Gravekeeper thread initialized")
     (sleep 30) ; wait for bots to start before looping
     (define (loop)
       (define num-bots-alive (length (get-all-resources thread?)))
       (gk-log (format "Threads active: ~a/~a" num-bots-alive total-bots))
       (when (not (eqv? num-bots-alive total-bots))
         (end-all-bots)
         (start-all-bots))
       (sleep 300) ; number of seconds the gravekeeper should sleep
       (loop))
     (loop))))

; basically an infinite loop/wait
(thread-wait main-t)

