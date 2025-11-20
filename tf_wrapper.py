import os
import sys
import re
from python_terraform import Terraform, IsFlagged

# --- Configuration ---
# Check if a directory path was provided as an argument
if len(sys.argv) < 2:
    print("Usage: python3 tf_wrapper.py <path/to/terraform/directory>")
    sys.exit(1)

# Set the path to the directory containing your main.tf, provider.tf, etc.
# The path is passed as the first command-line argument (sys.argv[1])
TERRAFORM_DIR = os.path.abspath(sys.argv[1])

def run_terraform_workflow():
    """
    Initializes Terraform, runs a plan, and applies the configuration.
    This function now contains the full workflow logic.
    """
    
    print(f"--- Starting Terraform Automation in directory: {TERRAFORM_DIR} ---")

    # 1. Initialize the Terraform object
    tf = Terraform(working_dir=TERRAFORM_DIR)

    try:
        # --- 2. Initialize (terraform init) ---
        print("\n[STEP 1/4] Running: terraform init")
        return_code, stdout, stderr = tf.init(
            capture_output=True, 
            reconfigure=IsFlagged
        )

        if return_code != 0:
            print("\n!!! ERROR: Terraform Init Failed !!!")
            print(stderr)
            sys.exit(1)
        print("Initialization successful.")

        # --- 3. Plan (terraform plan) ---
        print("\n[STEP 2/4] Running: terraform plan")
        
        return_code, stdout, stderr = tf.plan(
            capture_output=True,
            detailed_exitcode=True
        )

        # Print the plan output regardless of exit code
        print(stdout) 
        
        # Debug: Print the actual return code
        print(f"\n[DEBUG] Plan returned exit code: {return_code}")
        
        # Check for errors
        if return_code == 1 or (stderr and "Error:" in stderr):
            print("\n!!! ERROR: Terraform Plan Failed !!!")
            if stderr:
                print(stderr)
            sys.exit(1)
        
        # Parse the plan output to detect changes
        # Looking for: "Plan: X to add, Y to change, Z to destroy"
        has_changes = False
        to_add = 0
        to_change = 0
        to_destroy = 0
        
        plan_match = re.search(r'Plan:\s+(\d+)\s+to\s+add,\s+(\d+)\s+to\s+change,\s+(\d+)\s+to\s+destroy', stdout)
        if plan_match:
            to_add = int(plan_match.group(1))
            to_change = int(plan_match.group(2))
            to_destroy = int(plan_match.group(3))
            has_changes = (to_add + to_change + to_destroy) > 0
            print(f"\n[PARSE] Detected from plan output: {to_add} to add, {to_change} to change, {to_destroy} to destroy")
        else:
            print("\n[PARSE] Could not parse plan output for change detection")
            # If we can't parse but exit code is 2, trust the exit code
            if return_code == 2:
                has_changes = True
                print("[PARSE] Exit code is 2, assuming changes exist")
        
        if not has_changes:
            print("\n[INFO] Plan successful. No changes detected - infrastructure is up to date.")
            print("--- Terraform Workflow Completed Successfully (No Changes Needed) ---")
            return
        
        print("\n[INFO] Plan successful. Changes detected. Proceeding to Apply...")

        # --- 4. Apply (terraform apply -auto-approve) ---
        print("\n[STEP 3/4] Running: terraform apply")
        print("--- Streaming Output ---")
        
        return_code, stdout, stderr = tf.apply(
            capture_output=False, 
            skip_plan=True,
            auto_approve=IsFlagged
        )

        if return_code != 0:
            print("\n!!! ERROR: Terraform Apply Failed !!!")
            if stderr: 
                print(stderr)
            sys.exit(1)
        
        print("\n--- Apply Complete ---")

        # --- 5. Retrieve Outputs ---
        print("\n[STEP 4/4] Retrieving outputs...")
        outputs = tf.output()
        
        if outputs:
            print("\n--- Deployment Outputs ---")
            vpc_id = outputs.get('vpc_id', {}).get('value', 'N/A')
            public_subnets = outputs.get('public_subnet_ids', {}).get('value', 'N/A')

            print(f"VPC ID: {vpc_id}")
            print(f"Public Subnet IDs: {public_subnets}")
            print("\n--------------------------")
        else:
            print("No outputs found.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("\n--- Terraform Workflow Completed Successfully ---")


def run_plan_only(tf):
    """Initializes Terraform and runs only the plan command."""
    print("Running Terraform Init...")
    
    # Capture the return code from init
    init_return_code, init_stdout, init_stderr = tf.init(
        capture_output=True, 
        reconfigure=IsFlagged
    )
    
    # Check if init succeeded
    if init_return_code != 0:
        print("\n!!! ERROR: Terraform Init Failed !!!")
        print(init_stdout)
        print(init_stderr)
        sys.exit(1)
    
    print("Initialization successful.")
    print(init_stdout)
    
    print("Running Terraform Plan...")
    # Use detailed_exitcode=True to get 0 (no changes), 1 (failure), or 2 (changes)
    return_code, stdout, stderr = tf.plan(
        capture_output=True, 
        detailed_exitcode=True
    )
    
    # Print the output
    print(stdout)
    if stderr:
        print(stderr)
    
    print(f"\n[DEBUG] Plan exit code: {return_code}")
    
    # Return the exit code for the Bash script to capture 
    sys.exit(return_code)

    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tf_wrapper.py <path/to/terraform/directory>")
        sys.exit(1)
    
    TERRAFORM_DIR = os.path.abspath(sys.argv[1])
    
    if len(sys.argv) > 2 and sys.argv[2] == '--plan-only':
        tf = Terraform(working_dir=TERRAFORM_DIR)
        run_plan_only(tf) 
    else:
        run_terraform_workflow()