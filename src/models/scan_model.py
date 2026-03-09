# from datetime import datetime
# from bson import ObjectId

# from src.extensions import mongo


# def _to_objectid(x: str):
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def serialize_scan(doc: dict) -> dict:
#     if not doc:
#         return None

#     return {
#         "id": str(doc.get("_id")),
#         "userId": doc.get("userId", ""),
#         "fileName": doc.get("fileName", ""),
#         "imageUrl": doc.get("imageUrl", ""),
#         "createdAt": doc.get("createdAt", ""),
#         "updatedAt": doc.get("updatedAt", ""),
#         "stage": doc.get("stage", ""),
#         "confidence": doc.get("confidence", None),
#         "probs": doc.get("probs", None),
#         "model": doc.get("model", ""),
#         "version": doc.get("version", ""),
#         "heatmapUrl": doc.get("heatmapUrl", ""),
#     }


# def create_scan(doc: dict):
#     now = datetime.utcnow().isoformat()

#     payload = {
#         "userId": doc.get("userId", ""),
#         "fileName": doc.get("fileName", ""),
#         "imageUrl": doc.get("imageUrl", ""),
#         "imagePath": doc.get("imagePath", ""),
#         "createdAt": doc.get("createdAt", now),
#         "updatedAt": doc.get("updatedAt", now),
#         "stage": doc.get("stage", ""),
#         "confidence": doc.get("confidence", None),
#         "probs": doc.get("probs", None),
#         "model": doc.get("model", ""),
#         "version": doc.get("version", ""),
#         "heatmapUrl": doc.get("heatmapUrl", ""),
#     }

#     ins = mongo.db.scans.insert_one(payload)
#     payload["_id"] = ins.inserted_id
#     return serialize_scan(payload)


# def list_scans_by_user(user_id: str, limit: int = 50):
#     rows = (
#         mongo.db.scans.find({"userId": user_id})
#         .sort("createdAt", -1)
#         .limit(limit)
#     )
#     return [serialize_scan(x) for x in rows]


# def get_scan_by_id(user_id: str, scan_id: str):
#     oid = _to_objectid(scan_id)
#     if not oid:
#         return None

#     row = mongo.db.scans.find_one({"_id": oid, "userId": user_id})
#     return serialize_scan(row) if row else None


# def get_raw_scan_by_id(user_id: str, scan_id: str):
#     oid = _to_objectid(scan_id)
#     if not oid:
#         return None
#     return mongo.db.scans.find_one({"_id": oid, "userId": user_id})


# def delete_scan_by_id(user_id: str, scan_id: str):
#     oid = _to_objectid(scan_id)
#     if not oid:
#         return 0
#     result = mongo.db.scans.delete_one({"_id": oid, "userId": user_id})
#     return result.deleted_count


# def update_prediction(user_id: str, scan_id: str, pred: dict) -> bool:
#     oid = _to_objectid(scan_id)
#     if not oid:
#         return False

#     result = mongo.db.scans.update_one(
#         {"_id": oid, "userId": user_id},
#         {
#             "$set": {
#                 "stage": pred.get("stage", ""),
#                 "confidence": pred.get("confidence"),
#                 "probs": pred.get("probs"),
#                 "model": pred.get("model", ""),
#                 "version": pred.get("version", ""),
#                 "heatmapUrl": pred.get("heatmapUrl", ""),
#                 "updatedAt": datetime.utcnow().isoformat(),
#             }
#         },
#     )
#     return result.modified_count > 0 or result.matched_count > 0

from datetime import datetime
from bson import ObjectId

from src.extensions import mongo


def _to_objectid(x: str):
    try:
        return ObjectId(x)
    except Exception:
        return None


def serialize_scan(doc: dict) -> dict:
    if not doc:
        return None

    return {
        "id": str(doc.get("_id")),
        "userId": doc.get("userId", ""),
        "fileName": doc.get("fileName", ""),
        "imageUrl": doc.get("imageUrl", ""),
        "createdAt": doc.get("createdAt", ""),
        "updatedAt": doc.get("updatedAt", ""),
        "stage": doc.get("stage", ""),
        "confidence": doc.get("confidence", None),
        "probs": doc.get("probs", None),
        "model": doc.get("model", ""),
        "version": doc.get("version", ""),
        "heatmapUrl": doc.get("heatmapUrl", ""),
    }


def create_scan(doc: dict):
    now = datetime.utcnow().isoformat()

    payload = {
        "userId": doc.get("userId", ""),
        "fileName": doc.get("fileName", ""),
        "imageUrl": doc.get("imageUrl", ""),
        "imagePath": doc.get("imagePath", ""),
        "createdAt": doc.get("createdAt", now),
        "updatedAt": doc.get("updatedAt", now),
        "stage": doc.get("stage", ""),
        "confidence": doc.get("confidence", None),
        "probs": doc.get("probs", None),
        "model": doc.get("model", ""),
        "version": doc.get("version", ""),
        "heatmapUrl": doc.get("heatmapUrl", ""),
    }

    ins = mongo.db.scans.insert_one(payload)
    payload["_id"] = ins.inserted_id
    return serialize_scan(payload)


def list_scans_by_user(user_id: str, limit: int = 50):
    rows = mongo.db.scans.find({"userId": user_id}).sort("createdAt", -1).limit(limit)
    return [serialize_scan(x) for x in rows]


def get_scan_by_id(user_id: str, scan_id: str):
    oid = _to_objectid(scan_id)
    if not oid:
        return None

    row = mongo.db.scans.find_one({"_id": oid, "userId": user_id})
    return serialize_scan(row) if row else None


def get_raw_scan_by_id(user_id: str, scan_id: str):
    oid = _to_objectid(scan_id)
    if not oid:
        return None
    return mongo.db.scans.find_one({"_id": oid, "userId": user_id})


def delete_scan_by_id(user_id: str, scan_id: str):
    oid = _to_objectid(scan_id)
    if not oid:
        return 0
    result = mongo.db.scans.delete_one({"_id": oid, "userId": user_id})
    return result.deleted_count


def update_prediction(user_id: str, scan_id: str, pred: dict) -> bool:
    oid = _to_objectid(scan_id)
    if not oid:
        return False

    result = mongo.db.scans.update_one(
        {"_id": oid, "userId": user_id},
        {
            "$set": {
                "stage": pred.get("stage", ""),
                "confidence": pred.get("confidence"),
                "probs": pred.get("probs"),
                "model": pred.get("model", ""),
                "version": pred.get("version", ""),
                "heatmapUrl": pred.get("heatmapUrl", ""),
                "updatedAt": datetime.utcnow().isoformat(),
            }
        },
    )
    return result.modified_count > 0 or result.matched_count > 0