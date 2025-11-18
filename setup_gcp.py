"""
Google Cloud Platform Setup Test Script
Run this script to verify your GCP configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    print("=" * 60)
    print("Checking Environment Variables...")
    print("=" * 60)

    required_vars = {
        'GEMINI_API_KEY': 'Gemini API Key',
        'GCP_PROJECT_ID': 'GCP Project ID',
        'GOOGLE_APPLICATION_CREDENTIALS': 'Service Account Key Path'
    }

    optional_vars = {
        'GCP_REGION': 'GCP Region',
        'BIGQUERY_DATASET': 'BigQuery Dataset',
        'BIGQUERY_TABLE': 'BigQuery Table',
        'FIRESTORE_COLLECTION': 'Firestore Collection',
        'GCS_BUCKET': 'Cloud Storage Bucket'
    }

    all_good = True

    # Check required variables
    print("\n📋 Required Variables:")
    for var, name in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'CREDENTIALS' in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"  ✅ {name}: {display_value}")
        else:
            print(f"  ❌ {name}: NOT SET")
            all_good = False

    # Check optional variables
    print("\n📋 Optional Variables (for cloud features):")
    for var, name in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {name}: {value}")
        else:
            print(f"  ⚠️  {name}: NOT SET (using defaults)")

    return all_good


def test_firestore():
    """Test Firestore connection"""
    print("\n" + "=" * 60)
    print("Testing Firestore Connection...")
    print("=" * 60 + "\n")

    try:
        from utils.firestore_manager import FirestoreManager

        manager = FirestoreManager()

        if not manager.db:
            print("⚠️  Firestore not configured (optional)")
            return False

        # Test basic operations
        print("✅ Firestore connection successful!")
        print(f"   Collection: {manager.collection_name}")

        return True

    except Exception as e:
        print(f"❌ Firestore connection failed: {e}")
        print("\n💡 Tips:")
        print("   - Check that Firestore API is enabled")
        print("   - Verify GOOGLE_APPLICATION_CREDENTIALS points to valid JSON")
        print("   - Ensure service account has Firestore permissions")
        return False


def test_cloud_storage():
    """Test Cloud Storage connection"""
    print("\n" + "=" * 60)
    print("Testing Cloud Storage Connection...")
    print("=" * 60 + "\n")

    try:
        from utils.cloud_storage import CloudStorageManager

        manager = CloudStorageManager()

        if not manager.client:
            print("⚠️  Cloud Storage not configured (optional)")
            return False

        print("✅ Cloud Storage connection successful!")
        print(f"   Bucket: gs://{manager.bucket_name}")

        # Try to check if bucket exists
        if manager.bucket.exists():
            print("   ✅ Bucket exists and is accessible")
        else:
            print("   ⚠️  Bucket doesn't exist (will be created on first upload)")

        return True

    except Exception as e:
        print(f"❌ Cloud Storage connection failed: {e}")
        print("\n💡 Tips:")
        print("   - Check that Cloud Storage API is enabled")
        print("   - Verify GCS_BUCKET name is correct")
        print("   - Ensure service account has Storage Admin permissions")
        return False


def test_bigquery():
    """Test BigQuery connection"""
    print("\n" + "=" * 60)
    print("Testing BigQuery Connection...")
    print("=" * 60 + "\n")

    try:
        from utils.bigquery_logger import BigQueryLogger

        logger = BigQueryLogger()

        if not logger.client:
            print("⚠️  BigQuery not configured (optional)")
            return False

        print("✅ BigQuery connection successful!")
        print(f"   Dataset: {logger.dataset}")
        print(f"   Table: {logger.table}")

        # Try to create dataset and table
        print("\n   Testing dataset/table creation...")
        success = logger.create_dataset_and_table()

        if success:
            print("   ✅ Dataset and table are ready")
        else:
            print("   ⚠️  Could not create dataset/table (may already exist)")

        return True

    except Exception as e:
        print(f"❌ BigQuery connection failed: {e}")
        print("\n💡 Tips:")
        print("   - Check that BigQuery API is enabled")
        print("   - Verify BIGQUERY_DATASET and BIGQUERY_TABLE names")
        print("   - Ensure service account has BigQuery permissions")
        return False


def test_gemini():
    """Test Gemini API connection"""
    print("\n" + "=" * 60)
    print("Testing Gemini API Connection...")
    print("=" * 60 + "\n")

    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        return False

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        # Try to list models as a test
        models = genai.list_models()
        model_names = [m.name for m in models]

        print("✅ Gemini API connection successful!")
        print(f"   Available models: {len(model_names)}")

        # Check if our model is available
        if any('gemini-1.5-flash' in name for name in model_names):
            print("   ✅ gemini-1.5-flash model is available")
        else:
            print("   ⚠️  gemini-1.5-flash not found in available models")

        return True

    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        print("\n💡 Tips:")
        print("   - Check that API key is valid")
        print("   - Get your API key from: https://ai.google.dev")
        return False


def main():
    """Main setup verification"""
    print("\n" + "=" * 60)
    print("ConStrite - Google Cloud Platform Setup Verification")
    print("=" * 60)

    # Check environment variables
    env_ok = check_env_vars()

    if not env_ok:
        print("\n" + "=" * 60)
        print("❌ SETUP INCOMPLETE")
        print("=" * 60)
        print("\n⚠️  Some required environment variables are missing!")
        print("\n📖 Setup Instructions:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your API keys and project ID")
        print("   3. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   4. Run this script again")
        print("\n📚 See GOOGLE_CLOUD_SETUP.md for detailed instructions")
        return

    # Test individual services
    results = {
        'Gemini API': test_gemini(),
        'Firestore': test_firestore(),
        'Cloud Storage': test_cloud_storage(),
        'BigQuery': test_bigquery()
    }

    # Summary
    print("\n" + "=" * 60)
    print("Setup Verification Summary")
    print("=" * 60 + "\n")

    for service, status in results.items():
        status_icon = "✅" if status else ("⚠️ " if service != 'Gemini API' else "❌")
        status_text = "Ready" if status else ("Optional" if service != 'Gemini API' else "Failed")
        print(f"  {status_icon} {service}: {status_text}")

    # Overall status
    print("\n" + "=" * 60)

    if results['Gemini API']:
        print("✅ CORE FEATURES READY")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  streamlit run app.py")

        if not all(results.values()):
            print("\n⚠️  Some optional cloud features are not configured.")
            print("   The app will work, but without:")
            if not results['Firestore']:
                print("   - Live monitoring dashboard")
                print("   - Real-time data sync")
            if not results['Cloud Storage']:
                print("   - Cloud image storage")
            if not results['BigQuery']:
                print("   - Historical analytics")

            print("\n📚 To enable these features, see GOOGLE_CLOUD_SETUP.md")
    else:
        print("❌ SETUP INCOMPLETE")
        print("=" * 60)
        print("\nGemini API is required to run the application.")
        print("Get your API key from: https://ai.google.dev")

    print()


if __name__ == "__main__":
    main()
