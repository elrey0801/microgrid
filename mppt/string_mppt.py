from single_mppt import Panel
import time, random

V_D = 0.7

class String:
    def __init__(self, irradiances: list[float]):
        self.panels = [Panel(i) for i in irradiances]
        self.i_max = max(p.i_sc for p in self.panels)
        self.active_panels = sorted([p for p in self.panels if not p.bypass], key=lambda p: p.i_sc)
    
    def get_V(self, i):
        return sum(p.get_V(i) for p in self.panels)
    
    def get_P(self, i):
        return sum(p.get_V(i) * i for p in self.panels)
           
    def dp_di(self, i, step=1e-3):
        di = step
        p_0 = self.get_P(i)
        p_1 = self.get_P(i + di)
        dp = p_1 - p_0
        return dp / di
    
    def string_mppt(self, tol=1e-3):
        # knees = self.find_knees()
        peak = -1
        peak_i = -1
        prev_knee = 0
        for p in self.active_panels:
            left = prev_knee
            right = p.i_sc
            print(f"Searching between {left:.2f} A and {right:.2f} A for panel with Isc={p.i_sc:.2f} A")
            while True:
                half = (left + right) / 2
                dp_di = self.dp_di(half)
                print(f"left: {left:.2f}, right: {right:.2f}, half: {half:.2f}, dp_di: {dp_di:.2f}")
                if abs(dp_di) < tol or right - left < tol:
                    current_p = self.get_P(half)
                    if current_p > peak:
                        peak = current_p
                        peak_i = half
                    break
                if dp_di > 0:
                    left = half
                else:
                    right = half
            
            prev_knee = p.i_sc
        
        return peak, peak_i
    
string = String([random.randint(10,100) for _ in range(20)])
# string = String([100, 95, 90, 85, 20, 15, 10, 5])
start = time.perf_counter()
mpp = string.string_mppt(tol=0.01)
end = time.perf_counter()
print(f"Time taken: {end - start:.6f} seconds")
print(f"String MPPT I: {mpp[1]:.2f} A, String MPPT P: {mpp[0]:.2f} W")
                