DEBUG_PATH = "../logs/logfile.txt"
STEP_TYPE = ['CREATE', 'CLEAN', 'GEN_TREE', 'ENCODE']

def save_errors(enabled, error_count, error_list, step):
    if not enabled:
        return

    with open(DEBUG_PATH, 'a') as error_file_handle:
        error_file_handle.write(f"\nErrors during step: {STEP_TYPE[step-1]}\n")
        error_file_handle.write(f"=======================\n")
        error_file_handle.write(f"Total of {error_count} errors during creation process\n")
        for error in error_list:
            error_file_handle.write(f"{error}\n")
        error_file_handle.write(f"=======================\n")