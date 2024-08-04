I'm noticing that the `dateutil.parser.parse` is a bottleneck in some of my
scripts, and I sought to investigate if there are any speedups that might be
possible. I've inserted profile decorators using the line-profiler package to 
investigate where the slow parts of the code are, and I've found that 
`dateutil.parser._timelex.split` has a large footprint, with
`dateutil.parser._timelex.get_token` looking like it has the most potential for
optimization.


One immediate thing I noticed is that there are a lot of method calls to
one-line functions, that area really just aliases for string methods, although
they do enhance readability. But I wondered if there was a significant speedup
possible by sacrificing some readability., So I inserted two calls in a hot
section of the code to the `self.getword(nextchar)` method as well as its
inline form `nextchar.isalpha`, and measured a significant speedup by removing
the extra call overhead.


```
   124    450000   83274344.0    185.1      3.8                  nextchar.isalpha()
   125    450000  150698960.0    334.9      6.9                  self.isword(nextchar)
```

However, this code is running under line-profiler, so we need to see if there
is a speedup achieved outside of the profiling context. 

Using 100 loops with a best of 10, over 100 parsings of random 

With line profiler on, and using my benchmark the best loop iteration took
22.121 ms, and with the inline optimizations the best time was 20.690ms per
loop. This is a 6.469% speedup.

With line profile off the results are better. I increased the number of loops to 1000. 
The original code runs at 2.485 ms per loop and the inline code hits 2.221 ms
per loop which is 10.59% faster.
Details from the script output for a second run are:

```
Timed original for: 1000 loops, best of 10
    body took: 2.562 s
    time per loop: best=2.431 ms, mean=2.480 ± 0.0 ms

Timed alternative for: 1000 loops, best of 10
    body took: 2.271 s
    time per loop: best=2.185 ms, mean=2.206 ± 0.0 ms

min(percent_faster)=10.088560162984272%
mean(percent_faster)=11.049236678221678%
```
