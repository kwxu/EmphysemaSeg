import os
import pandas as pd
from tqdm import tqdm


def generate_experimental_t0_data(n_case=10):
    chest_extra_project_root = '/nfs/masi/xuk9/Projects/ChestExtrapolation'

    data_dir = os.path.join(chest_extra_project_root, 'LobeSeg/Experimental')
    os.makedirs(data_dir, exist_ok=True)

    use_data_csv = os.path.join(chest_extra_project_root, 'Data.T0', 'use_case_record.csv')
    print(f'Load {use_data_csv}')
    use_data_df = pd.read_csv(use_data_csv)

    in_t0_data_dir = '/nfs2/NLST/NIfTI/T0_all'
    out_ct_dir = os.path.join(data_dir, 'data/nifti')
    os.makedirs(out_ct_dir, exist_ok=True)

    for index, use_data_record in use_data_df.head(n_case).iterrows():
        series_uid = use_data_record['series_uid']

        in_nii = os.path.join(in_t0_data_dir, f'{series_uid}.nii.gz')
        out_nii = os.path.join(out_ct_dir, f'{series_uid}.nii.gz')

        ln_cmd = f'ln -sf {in_nii} {out_nii}'
        os.system(ln_cmd)


def generate_all_t0_data():
    chest_extra_project_root = '/nfs/masi/xuk9/Projects/ChestExtrapolation'

    data_dir = os.path.join(chest_extra_project_root, 'LobeSeg/T0_all')
    os.makedirs(data_dir, exist_ok=True)

    use_data_csv = os.path.join(chest_extra_project_root, 'Data.T0', 'use_case_record.csv')
    print(f'Load {use_data_csv}')
    use_data_df = pd.read_csv(use_data_csv)

    in_t0_data_dir = '/nfs2/NLST/NIfTI/T0_all'
    out_ct_dir = os.path.join(data_dir, 'data/nifti')
    os.makedirs(out_ct_dir, exist_ok=True)

    for index, use_data_record in tqdm(use_data_df.iterrows(), total=len(use_data_df.index)):
        series_uid = use_data_record['series_uid']

        in_nii = os.path.join(in_t0_data_dir, f'{series_uid}.nii.gz')
        out_nii = os.path.join(out_ct_dir, f'{series_uid}.nii.gz')

        ln_cmd = f'ln -sf {in_nii} {out_nii}'
        os.system(ln_cmd)


def generate_t1_t2_data():
    chest_extra_project_root = '/local_ssd1/xuk9/Projects/ChestExtrapolation'

    for sess_id in [1, 2]:
        data_dir = os.path.join(chest_extra_project_root, f'LobeSeg/T{sess_id}_all')
        os.makedirs(data_dir, exist_ok=True)

        use_data_csv = os.path.join(chest_extra_project_root, f'Data.T{sess_id}', 'use_case_record.csv')
        print(f'Load {use_data_csv}')
        use_data_df = pd.read_csv(use_data_csv)

        in_t0_data_dir = f'/local_storage2/Data/NLST/NIfTI/T{sess_id}_all'
        out_ct_dir = os.path.join(data_dir, 'data/nifti')
        os.makedirs(out_ct_dir, exist_ok=True)

        for index, use_data_record in tqdm(use_data_df.iterrows(), total=len(use_data_df.index)):
            series_uid = use_data_record['series_uid']

            in_nii = os.path.join(in_t0_data_dir, f'{series_uid}.nii.gz')
            out_nii = os.path.join(out_ct_dir, f'{series_uid}.nii.gz')

            ln_cmd = f'ln -sf {in_nii} {out_nii}'
            os.system(ln_cmd)



if __name__ == '__main__':
    # generate_experimental_t0_data()
    # generate_all_t0_data()
    generate_t1_t2_data()

