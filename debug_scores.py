import utils
import os

jd_path = os.path.abspath("sample_data/JD_SoftwareEngineer.txt")
r1_path = os.path.abspath("sample_data/Resume_Vanitha_HighMatch.txt")
r2_path = os.path.abspath("sample_data/Resume_Mritto_MediumMatch.txt")
r3_path = os.path.abspath("sample_data/Resume_Shyan_LowMatch.txt")

print(f"JD Path: {jd_path}")

try:
    jd_text = utils.extract_text(jd_path)
    r1_text = utils.extract_text(r1_path)
    r2_text = utils.extract_text(r2_path)
    r3_text = utils.extract_text(r3_path)

    print(f"JD Text Length: {len(jd_text)}")
    print(f"Vanitha Text Length: {len(r1_text)}")
    print(f"Mritto Text Length: {len(r2_text)}")
    print(f"Shyan Text Length: {len(r3_text)}")
    
    # Process
    proc_jd = utils.preprocess_text(jd_text)
    proc_r1 = utils.preprocess_text(r1_text)
    proc_r2 = utils.preprocess_text(r2_text)
    proc_r3 = utils.preprocess_text(r3_text)

    scores = utils.calculate_similarity(proc_jd, [proc_r1, proc_r2, proc_r3])
    
    print("\n--- Scores ---")
    print(f"Vanitha (High): {scores[0] * 100:.2f}%")
    print(f"Mritto (Medium): {scores[1] * 100:.2f}%")
    print(f"Shyan (Low): {scores[2] * 100:.2f}%")

except Exception as e:
    print(f"Error: {e}")
