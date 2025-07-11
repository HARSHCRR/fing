import base64
import struct
import math

# ——— 1. Decode Base64 to raw ISO bytes ———
def decode_template(b64str: str) -> bytes:
    return base64.b64decode(b64str)

# ——— 2. Parse ISO‐19794‑2 minutiae from raw bytes ———
def read_iso_minutiae_from_bytes(data: bytes) -> list[tuple[int,int,int]]:
    header_len = 26  
    num_min = struct.unpack_from('>H', data, header_len)[0]
    print(f"[DEBUG] Data length: {len(data)}")
    print(f"[DEBUG] Minutiae count: {num_min}")
    minutiae = []
    off = header_len + 2
    for i in range(num_min):
        if off + 6 > len(data):
            print(f"[DEBUG] Not enough bytes for minutia {i} at offset {off}. Stopping early.")
            break
        x, y, theta, mtype = struct.unpack_from('>HHBB', data, off)
        minutiae.append((x, y, theta))
        off += 6
    print(f"[DEBUG] Parsed {len(minutiae)} minutiae.")
    return minutiae

# ——— 3. Brute‐force a match score between two minutiae sets ———
def match_score(m1, m2, radius=15, ang_tol=10):
    best = 0
    for (x1,y1,a1) in m1:
        for (x2,y2,a2) in m2:
            dtheta = math.radians(a2 - a1)
            count = 0
            for (x,y,a) in m1:
                # align point → rotate + translate
                xr = math.cos(dtheta)*(x - x1) - math.sin(dtheta)*(y - y1) + x2
                yr = math.sin(dtheta)*(x - x1) + math.cos(dtheta)*(y - y1) + y2
                ath = (a + (a2 - a1)) % 360
                # look for a matching minutia in m2
                for (u,v,b) in m2:
                    if abs(xr - u) <= radius and abs(yr - v) <= radius \
                       and min(abs(ath-b), 360-abs(ath-b)) <= ang_tol:
                        count += 1
                        break
            best = max(best, count)
    return best

# ——— 4. Plug in your two Base64 templates here ———
template1_b64 = "Rk1SACAyMAAAAAEyAAABAAGQAMUAxQEAAABTLkCTABj8UIByACmAUIBkACsAUEDlADf8PEByAEDwXUBBAEf0UICMAFrkXYCoAFr0UEBaAFzoXUDEAFx4UIDbAGGMSoA1AGHoUECAAGPcXUDuAGiUSoDEAG+EXUB0AHbIXYDsAHaYUECTAHvIXYBiAH3MUICHAITEXUC/AISYXYBrAJlQUIBDAJ7UXYCaAKA4XYA6AKXUXUCOAKw8XYA1ALrUXUClALooXUB0AMaEXYAuAMjUXYDwAMicQ4BiANQEXUDUANYgXUAPANvUXYApAOvUUIBYAPD0XYApAPJQUEApAQzgXUDwAQywQ4DlARGkUEBMASFkXYDZAU6YQ0CxAVcYXUBRAXH0XUBwAXF4XUApAXjkUAAA"
template2_b64 = "Rk1SACAyMAAAAAD2AAABAAGQAMUAxQEAAABRJECHAC3wV0BYADL0V4ChAEDkV0DeAEV4SkByAEnoV0DCAEn4V0BKAE7kV0CVAE7cV4DZAFqASoCMAFzMXUDzAF+kSoCtAGPMXYChAGrEXUDXAG2YXYBdAIbUXYCvAIs8XYBRAJDUXUCjAJc4XYCHAJssV4BKAKLQXUC9AKIsXYBDAK7QXYANALhYQ0B5ALgAUEAlAMHUV4BwANbwXYBBAPDgXYASAQBcV4BkAQdoXYDnAQqcUIDlAR8UQ0DuAS2wPEDJAUAUV0CFAVd4XUBpAVn0XUBDAWPoXQAA"
# ——— 5. Run decode → parse → match → threshold test ———
m1 = read_iso_minutiae_from_bytes(decode_template(template1_b64))
m2 = read_iso_minutiae_from_bytes(decode_template(template2_b64))
score = match_score(m1, m2)
print(f"Match score: {score}")

# Choose your threshold (e.g. 12)
if score >= 12:
    print("✅ FINGERPRINTS MATCH")
else:
    print("❌ NO MATCH")
