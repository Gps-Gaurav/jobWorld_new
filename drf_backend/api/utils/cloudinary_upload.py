import cloudinary.uploader

def upload_to_cloudinary(file):
    try:
        result = cloudinary.uploader.upload(file, folder="logos")
        return result.get("secure_url")
    except Exception as e:
        print("Cloudinary upload error:", e)
        return None
