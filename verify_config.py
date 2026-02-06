import os
from dotenv import load_dotenv

def verify():
    print("--- Environment Verification ---")
    
    # 1. Check if .env exists
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        print(f"✅ Found .env file at: {env_path}")
    else:
        print(f"❌ .env file NOT FOUND at: {env_path}")
        return

    # 2. Load .env
    load_dotenv()
    
    # 3. Check specific variables (masked for safety)
    vars_to_check = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_JWT_SECRET"
    ]
    
    all_present = True
    for var in vars_to_check:
        val = os.getenv(var)
        if not val:
            print(f"❌ {var} is MISSING")
            all_present = False
        elif val == "your_jwt_secret_here" or "your-" in val:
            print(f"⚠️  {var} is still using a PLACEHOLDER value")
            all_present = False
        else:
            masked = val[:5] + "..." + val[-5:] if len(val) > 10 else "***"
            print(f"✅ {var} is present (Value: {masked})")
            
    if all_present:
        print("\n🎉 Everything looks configured correctly!")
    else:
        print("\n🔧 Please update your .env file with the values from your Supabase Dashboard.")

if __name__ == "__main__":
    verify()
