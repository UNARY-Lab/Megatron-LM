#!/usr/bin/env python3

import pandas as pd
import numpy as np
import fire
import ijson
import os
import time


def geo_mean(data):
    return np.exp(np.log(data).mean())


def arith_mean(data):
    return data.mean()


def old_main(rocprof_csv_filename: str, pytorch_json_filename: str):
    rocprof_df = pd.read_csv(rocprof_csv_filename)

    mfma_mask = rocprof_df.get('SQ_INSTS_MFMA') != 0
    rocclr_mask = rocprof_df.get('KernelName').str.contains('rocclr')
    # mask = rocclr_mask
    mask = mfma_mask
    # mask = mfma_mask & ~rocclr_mask
    mfma_insts = np.count_nonzero(mask)
    mfma_kernels = rocprof_df[mask]
    print(f"mask shape: {mask.shape}")
    perc_mfma_kernels = mfma_insts/mask.shape[0]*100
    print(f"% of kernels that issue MFMAs: {perc_mfma_kernels:.3f}%")

    sqc = np.sum(mfma_kernels.get("SQ_CYCLES"))
    sqbc = np.sum(mfma_kernels.get("SQ_BUSY_CYCLES"))
    p_sqbc_sqc = sqbc / sqc * 100
    print(f"% of busy cycles to cycles: {p_sqbc_sqc:.3f}%")

    sqbcc = np.sum(mfma_kernels.get("SQ_BUSY_CU_CYCLES"))*4
    p_sqbcc_sqbc = sqbcc / (sqbc << 6) * 100
    print(f"% of busy cu cycles to busy cycles: {p_sqbcc_sqbc:.3f}%")

    sqvmbc = np.sum(mfma_kernels.get("SQ_VALU_MFMA_BUSY_CYCLES"))
    p_sqvmbc_sqbcc = sqvmbc / sqbcc * 100
    print(f"% of busy MFMA cycles to busy CU cycles: {p_sqvmbc_sqbcc:.3f}%")

    # n_mfma_issue_all = np.sum(df.get("SQ_INSTS_MFMA"))
    # n_any_issue_all = np.sum(df.get("SQ_INSTS"))
    # perc_mfma_issue_all = n_mfma_issue_all / n_any_issue_all * 100
    # print(f"% of issued mfma instructions ALL kernels use: {perc_mfma_issue_all:.3f}%")
    # names = set(mfma_kernels.get("KernelName"))
    # print(names)


def check_for_pkl(filename: str):
    pkl_filename = f"{filename}.pkl"
    if not os.path.exists(pkl_filename):
        return None
    fn_mtime = os.path.getmtime(filename)
    pkl_mtime = os.path.getmtime(pkl_filename)
    if (pkl_mtime < fn_mtime):
        return None
    return pd.read_pickle(pkl_filename)


def main(rocprof_csv_filename: str, pytorch_json_filename: str):
    rocprof_df = check_for_pkl(rocprof_csv_filename)
    if rocprof_df is None:
        rocprof_df = pd.read_csv(rocprof_csv_filename)
        rocprof_df.to_pickle(f"{rocprof_csv_filename}.pkl")

    pytorch_df = check_for_pkl(pytorch_json_filename)
    if pytorch_df is None:
        pytorch_data = []
        with open(pytorch_json_filename, 'r') as pt_fp:
            json_state = 0
            kern_name = None
            ts = None
            dur = None
            parser = ijson.parse(pt_fp)
            for prefix, event, value in parser:
                if json_state == 0:
                    assert kern_name is None and ts is None and dur is None
                    if prefix == "traceEvents.item.name" and event == "string":
                        kern_name = value
                        json_state = 1
                elif json_state == 1:
                    assert kern_name is not None and ts is None and dur is None
                    if prefix == "traceEvents.item.ts" and event == "number":
                        ts = value
                        json_state = 2
                elif json_state == 2:
                    assert kern_name is not None and ts is not None and dur is None
                    if prefix == "traceEvents.item.dur" and event == "number":
                        dur = value
                        json_state = 0
                        pytorch_data.append((kern_name, ts, dur))
                        kern_name = None
                        ts = None
                        dur = None

        pytorch_df = pd.DataFrame(
            pytorch_data, columns=("KernelName", "Timestamp", "Duration"))
        pytorch_df.to_pickle(f"{pytorch_json_filename}.pkl")

    print(pytorch_df)
    return 0

    n_cu = 304
    mfma_busy = rocprof_df.get("SQ_VALU_MFMA_BUSY_CYCLES")
    grbm_gui_active = rocprof_df.get("GRBM_GUI_ACTIVE")
    mfma_efficiency = 100 * mfma_busy / (grbm_gui_active * n_cu * 4)
    mfma_eff_kern = pd.DataFrame(
        {
            "KernelName": rocprof_df.get("KernelName"),
            "MfmaUtil": mfma_efficiency
        })

    # summary_df = mfma_eff_kern.groupby("KernelName", as_index=False).agg(
    #     Average=("MfmaUtil", "mean"),
    #     Max=("MfmaUtil", "max"),
    #     Min=("MfmaUtil", "min")
    # ).sort_values(by="Average", ascending=False)
    summary_df = mfma_eff_kern.agg(
        Average=("MfmaUtil", "mean"),
        Max=("MfmaUtil", "max"),
        Min=("MfmaUtil", "min")
    ).sort_values(by="Average", ascending=False)

    print(summary_df)

    # n_mfma_issue_all = np.sum(df.get("SQ_INSTS_MFMA"))
    # n_any_issue_all = np.sum(df.get("SQ_INSTS"))
    # perc_mfma_issue_all = n_mfma_issue_all / n_any_issue_all * 100
    # print(f"% of issued mfma instructions ALL kernels use: {perc_mfma_issue_all:.3f}%")
    # names = set(mfma_kernels.get("KernelName"))
    # print(names)


if __name__ == "__main__":
    fire.Fire(main)
