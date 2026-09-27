import pvlib, time

class Panel:
    def __init__(self, effective_irradiance_percent: int):
        if effective_irradiance_percent == 0:
            self.i_sc = 0
            self.v_oc = 0
            self.bypass = True
            return
        if effective_irradiance_percent < 0 or effective_irradiance_percent > 100:
            raise ValueError("Effective irradiance percent must be between 0 and 100.")
        self.bypass = False
        effective_irradiance = effective_irradiance_percent * 1000 / 100
        self.IL, self.I0, self.Rs, self.Rsh, self.a = self.create_panel(effective_irradiance)
        self.irradiance = effective_irradiance
        self.i_sc = self.get_I(0)
        self.v_oc = self.get_V(0)
        
    def create_panel(self, effective_irradiance: int):
        p = pvlib.pvsystem.retrieve_sam('CECMod')['Kyocera_Solar_KC200GT']
        IL, I0, Rs, Rsh, a = pvlib.pvsystem.calcparams_cec(
            effective_irradiance=effective_irradiance,   # W/m2
            temp_cell=25,                # C
            alpha_sc=p['alpha_sc'], a_ref=p['a_ref'], I_L_ref=p['I_L_ref'],
            I_o_ref=p['I_o_ref'], R_sh_ref=p['R_sh_ref'], R_s=p['R_s'],
            Adjust=p['Adjust'])
        return IL, I0, Rs, Rsh, a

    def get_I(self, v):
        if self.bypass:
            return 0
        return pvlib.pvsystem.i_from_v(v, self.IL, self.I0, self.Rs, self.Rsh, self.a)
    
    def get_V(self, i):
        if self.bypass:
            return -0.7
        return max(pvlib.pvsystem.v_from_i(i, self.IL, self.I0, self.Rs, self.Rsh, self.a), -0.7)
    
    def dp_dv(self, v, step=1e-3):
        dv = step
        p_0 = self.get_I(v) * v
        p_1 = self.get_I(v + dv) * (v + dv)
        dp = p_1 - p_0
        return dp / dv

    def mppt(self, tol=1e-3):
        right = self.get_V(0)
        left = 0
        while True:
            half = (left + right) / 2
            i = self.get_I(half)
            dp_dv = self.dp_dv(half)
            print(f"left: {left:.2f}, right: {right:.2f}, half: {half:.2f}, i: {i:.2f}, di_dv: {dp_dv:.2f}")
            if abs(dp_dv) < tol:
                return half, i
            if dp_dv > 0:
                left = half
            else:
                right = half
                
        
if __name__ == "__main__":    
    panel = Panel(effective_irradiance=80)

    start = time.perf_counter()
    panel_mppt = panel.mppt()
    end = time.perf_counter()
    print(f"Time taken for MPPT: {end - start:.6f} seconds")
    print(f"MPPT Voltage: {panel_mppt[0]:.2f} V, MPPT Current: {panel_mppt[1]:.2f} A, MPPT Power: {panel_mppt[0] * panel_mppt[1]:.2f} W")

