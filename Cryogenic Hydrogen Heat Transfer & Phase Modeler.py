import numpy as np
import matplotlib.pyplot as plt

# Geometry
L_channel = 1.3               # Length of the fuel channel (meters)
nodes = 100                   # Number of spatial steps
dz = L_channel / nodes        # Length of each step (m)
z_array = np.linspace(0, L_channel, nodes)

D_channel = 0.0025            # Channel diameter (2.5 mm, standard NERVA size)
P_h = np.pi * D_channel       # Heated perimeter (m)

m_dot = 0.002                 # Mass flow rate per channel (kg/s)
P_core = 7.0e6                # Core Pressure (7 MPa / ~1000 psi)
q_flux = 3.5e6                # Wall heat flux (W/m^2) - Massive heat load

# Hyrdogen Thermodynamics at 7 MPa
T_boil = 33.0                 # Approximate transition/boiling temp at pressure (K)
R_H2 = 4124.0                 # Specific gas constant for H2 (J/kg-K)

def get_h2_properties(T):
    if T <= T_boil:
        # Liquid Phase Approximations
        Cp = 9000.0           # J/kg-K (Lower Cp for cryogenic liquid)
        rho = 71.0            # kg/m^3 (Dense liquid)
    else:
        # Gas Phase Approximations
        Cp = 14500.0          # J/kg-K (High Cp for H2 gas)
        rho = P_core / (R_H2 * T) # Ideal Gas Law for density
    return Cp, rho

# Solver
T_array = np.zeros(nodes)
rho_array = np.zeros(nodes)

# Inlet Conditions
T_array[0] = 20.0             # 20 K Cryogenic Inlet
_, rho_array[0] = get_h2_properties(T_array[0])

# Marching up the Z-axis
for i in range(nodes - 1):
    T_current = T_array[i]
    Cp_current, rho_current = get_h2_properties(T_current)
    
    # Calculate temperature rise for this slice: dT = (q'' * Perimeter * dz) / (m_dot * Cp)
    dT = (q_flux * P_h * dz) / (m_dot * Cp_current)
    
    # Update next node
    T_array[i+1] = T_current + dT
    _, rho_array[i+1] = get_h2_properties(T_array[i+1])

# Visualized Data
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Fluid Temperature
color1 = 'tab:red'
ax1.set_xlabel('Axial Position Along Fuel Channel (m)', fontweight='bold')
ax1.set_ylabel('Hydrogen Temperature (K)', color=color1, fontweight='bold')
ax1.plot(z_array, T_array, color=color1, linewidth=2.5, label='Temperature (K)')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, linestyle='--', alpha=0.6)

ax2 = ax1.twinx()  
color2 = 'tab:blue'
ax2.set_ylabel('Hydrogen Density (kg/m³)', color=color2, fontweight='bold')  
ax2.plot(z_array, rho_array, color=color2, linewidth=2.5, linestyle='-', label='Density (kg/m³)')
ax2.tick_params(axis='y', labelcolor=color2)

plt.title('NTP Fuel Channel: Cryogenic Heating & Density Drop', fontweight='bold', fontsize=14)
fig.tight_layout()  
plt.show()

print(f"--- Core Exit Conditions ---")
print(f"Exit Temperature: {T_array[-1]:.2f} K")
print(f"Exit Density: {rho_array[-1]:.4f} kg/m^3")