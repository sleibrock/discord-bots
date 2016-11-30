#lang racket

(require "src/supervisor.rkt")

(module+ test (require rackunit racket/port))

(module+ test
  (define (debug-args bot)
    (match (car bot)
      ("node"   (cons (car bot) (append '("-c") (cdr bot))))
      ("python" (cons (car bot) (append '("-m" "py_compile") (cdr bot))))))
  (define (sys->str cmd)  (with-output-to-string (λ () (syscall cmd)))))
                          
(module+ test
  (test-case "Test whether all packages have been installed"
    (let ([pip-out (sys->str '("pip" "freeze" "--disable-pip-version-check"))]
          [req-txt (port->lines (open-input-file "requirements.txt"))])
      (displayln "Checking if packages were installed...")
      (check <=
             (length req-txt)
             (length (filter non-empty-string? (string-split pip-out "\n")))))))

(module+ test 
   (test-case "Testing successful compiles on all bots"
     (let ([subs (map (λ (bot) (syscall (debug-args bot))) bots)])
       (displayln "Checking if all bots were properly tested...")
       (check = (length subs) total-bots)
       (displayln "Checking if all bots compiled successfully...")
       (for-each check-true subs)
       )))

; end
