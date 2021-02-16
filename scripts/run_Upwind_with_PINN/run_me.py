from sklearn.metrics import mean_absolute_error, mean_squared_error

from burgers_ml.PINN import PINN
from burgers_numerical.Upwind import Upwind
from util.generate_plots import *
import numpy as np

# Part 1: Build and train PINN
pinn = PINN()
pinn.generate_training_data(n_initial=50, n_boundary=25, equidistant=False)
pinn.perform_training(max_n_epochs=3000, min_mse=0.05, track_losses=True, batch_size='full')

# Plot solution
print(f"PINN error: {pinn.mse}")
print(pinn.loss_df)
# generate_contour_and_snapshots_plot(u=pinn.u_pred, savefig_path='scripts/run_Upwind_with_PINN/PINN_solution.jpg')


# Part 2: Use initial data generated by PINN and use them as IC for Upwind solver

n_spatial = 1281
n_temporal = 10**4 + 1

# Generate initial data for Upwind solver
feat = np.column_stack((np.linspace(-1, 1, n_spatial), np.zeros(n_spatial)))
initial_data = pinn.network(feat)[:, 0]

# Run solver
upwind = Upwind(n_spatial=n_spatial, n_temporal=n_temporal, u0=initial_data, order=2)
upwind.time_integrate()

# Get error and plot solution
print(f"Upwind L2 error: {upwind.get_l2_error()}")
print(f"Upwind L2 error squared: {upwind.get_l2_error()**2}")
print(f"Upwind MSE: {upwind.get_mean_squared_error()}")
# generate_contour_and_snapshots_plot(u=upwind.u_numerical, savefig_path='scripts/run_Upwind_with_PINN/Upwind_solution.jpg')

# ToDo: Change file name
# generate_two_contour_and_snapshots_plots(u1=pinn.u_pred, u2=upwind.u_numerical)
file_name = "PINN_vs_Upwind_epochs=3000.jpg"
generate_two_contour_and_snapshots_plots(u1=pinn.u_pred, u2=upwind.u_numerical, train_feat=pinn.train_feat,
                                         savefig_path=f'scripts/run_Upwind_with_PINN/{file_name}')

# Compute error between Upwind and PINN solution
x = np.linspace(-1, 1, n_spatial)
t = np.linspace(0, 1, n_temporal)
x_mesh, t_mesh = np.meshgrid(x, t)
eval_feat = np.hstack((x_mesh.flatten()[:, None], t_mesh.flatten()[:, None]))
pinn_u_pred = np.reshape(pinn.network(eval_feat), (n_temporal, n_spatial)).T

print(f"MAE(Upwind - PINN): {mean_absolute_error(pinn_u_pred, upwind.u_numerical)}")
print(f"MSE(Upwind - PINN): {mean_squared_error(pinn_u_pred, upwind.u_numerical)}")
print(f"L2(Upwind - PINN): {np.sqrt(mean_squared_error(pinn_u_pred, upwind.u_numerical))}")
