#lang racket

(require rackunit rackunit/text-ui "src/supervisor.rkt")

(define (debug-args program code)
  (match program
    ("node"   (list "-c" code))
    ("python" (list "-m" "py_compile" code))))

(define t
  (test-suite
   "Discord Bot Test Suite"
   #:before (lambda ()
             (displayln "Beginning tests")
             (displayln (format "Current directory: ~a" (current-directory))))
   #:after  (lambda () (displayln "Ending tests"))
   
   (test-case
       "Testing ability to kill subprocs"
     (let ([subs
            (build-list
             10
             (lambda (x)
                 (define-values (a b c d)
                   (subproc "sleep" '("300000")))
                     a))])
       (check = (length subs) 10 "Test size not equal")
       (for-each subproc-kill subs)
       (sleep 2) ; sleep to wait on the OS process killing
       (for-each
        (lambda (sub)
          (check-not-eq? 'running (subprocess-status sub)))
        subs)))
   
   (test-case
       "Testing successful compiles on all bots"
     (let ([subs
            (build-list
             total-bots
             (lambda (x)
                 (define-values (interp code) (apply values (vector-ref bots x)))
                 (define-values (a b c d) (subproc interp (debug-args interp code)))
                 a))])
       (check = (length subs) total-bots)
       (sleep 5)
       (for-each (lambda (sub) (check-eq? 0 (subprocess-status sub))) subs)
       0))
   ))
  
(run-tests t 'verbose)
