#lang racket

(module+ test (require rackunit racket/port "src/supervisor.rkt"))

(module+ test 
    (define (debug-args program code)
      (match program
        ("node"   (list "-c" code))
        ("python" (list "-m" "py_compile" code))))
    (define (syscall cmds)
      (parameterize ([current-subprocess-custodian-mode 'kill])
        (apply system* (append (list (find-executable-path (car cmds))) (cdr cmds)))))
    (define (sys->str cmd) (with-output-to-string (λ () (syscall cmd)))))

(module+ test
   (test-case "Testing ability to kill subprocs"
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
   
   (test-case "Testing successful compiles on all bots"
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

   (test-case "Test whether all packages have been installed"
     (let ([pip-out (sys->str '("pip" "freeze" "--disable-pip-version-check"))]
           [req-txt (port->lines (open-input-file "requirements.txt"))])
       (displayln "Checking if packages were installed...")
       (check <=
              (length req-txt)
              (length (filter non-empty-string? (string-split pip-out "\n"))))))
   )
; end
