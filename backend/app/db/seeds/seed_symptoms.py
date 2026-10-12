from backend.app.db.database import SessionLocal, engine
from backend.app.db.models import Symptom, Base

# Make sure tables exist
Base.metadata.create_all(bind=engine)

SYMPTOMS_LIST = [
    # --- Cardiovascular ---
    {"code": "chest_pain", "name": "Chest Pain", "category": "Cardiovascular", "is_red_flag": True, "description": "Pain or discomfort in the chest area, potentially radiating to the arm, shoulder, or jaw."},
    {"code": "palpitations", "name": "Palpitations", "category": "Cardiovascular", "is_red_flag": False, "description": "A sensation of rapid, strong, or irregular heartbeat."},
    {"code": "shortness_of_breath", "name": "Shortness of Breath", "category": "Cardiovascular", "is_red_flag": True, "description": "Difficulty breathing or feeling winded (dyspnea)."},
    {"code": "leg_edema", "name": "Swollen Legs / Edema", "category": "Cardiovascular", "is_red_flag": False, "description": "Swelling in the ankles, feet, or legs due to fluid buildup."},
    {"code": "dizziness", "name": "Dizziness / Lightheadedness", "category": "Cardiovascular", "is_red_flag": False, "description": "Feeling faint, woozy, or unsteady."},
    {"code": "fainting", "name": "Fainting / Syncope", "category": "Cardiovascular", "is_red_flag": True, "description": "Temporary loss of consciousness."},
    {"code": "cold_extremities", "name": "Cold Hands or Feet", "category": "Cardiovascular", "is_red_flag": False, "description": "Extremities feeling unusually cold to touch."},
    {"code": "claudication", "name": "Leg Pain on Walking", "category": "Cardiovascular", "is_red_flag": False, "description": "Pain in the calves or legs during physical exertion, relieved by rest."},
    {"code": "irregular_pulse", "name": "Irregular Pulse", "category": "Cardiovascular", "is_red_flag": False, "description": "Pulse feels inconsistent or skipped beats."},

    # --- Respiratory ---
    {"code": "cough", "name": "General Cough", "category": "Respiratory", "is_red_flag": False, "description": "Sudden, noisy expulsion of air from the lungs."},
    {"code": "dry_cough", "name": "Dry Cough", "category": "Respiratory", "is_red_flag": False, "description": "Cough without phlegm or mucus production."},
    {"code": "wet_cough", "name": "Wet Cough / Productive Cough", "category": "Respiratory", "is_red_flag": False, "description": "Cough that produces phlegm or mucus."},
    {"code": "wheezing", "name": "Wheezing", "category": "Respiratory", "is_red_flag": False, "description": "High-pitched whistling sound made while breathing."},
    {"code": "hemoptysis", "name": "Coughing Up Blood", "category": "Respiratory", "is_red_flag": True, "description": "Blood or blood-streaked mucus coughed up from the respiratory tract."},
    {"code": "sore_throat", "name": "Sore Throat", "category": "Respiratory", "is_red_flag": False, "description": "Pain, itchiness, or irritation in the throat."},
    {"code": "runny_nose", "name": "Runny Nose / Rhinorrhea", "category": "Respiratory", "is_red_flag": False, "description": "Excess nasal drainage."},
    {"code": "nasal_congestion", "name": "Nasal Congestion", "category": "Respiratory", "is_red_flag": False, "description": "Stuffy nose, difficulty breathing through the nose."},
    {"code": "sneezing", "name": "Sneezing", "category": "Respiratory", "is_red_flag": False, "description": "Involuntary, convulsive expulsion of air from the nose and mouth."},
    {"code": "chest_tightness", "name": "Chest Tightness", "category": "Respiratory", "is_red_flag": False, "description": "Sensation of pressure or constriction in the chest."},
    {"code": "stridor", "name": "Stridor", "category": "Respiratory", "is_red_flag": True, "description": "Harsh, vibrating noise during breathing, caused by obstruction of the windpipe."},

    # --- Gastrointestinal ---
    {"code": "nausea", "name": "Nausea", "category": "Gastrointestinal", "is_red_flag": False, "description": "Sensation of unease in the stomach with an urge to vomit."},
    {"code": "vomiting", "name": "Vomiting", "category": "Gastrointestinal", "is_red_flag": False, "description": "Forcible ejection of stomach contents through the mouth."},
    {"code": "diarrhea", "name": "Diarrhea", "category": "Gastrointestinal", "is_red_flag": False, "description": "Frequent, loose, or watery bowel movements."},
    {"code": "constipation", "name": "Constipation", "category": "Gastrointestinal", "is_red_flag": False, "description": "Infrequent or difficult bowel movements."},
    {"code": "abdominal_pain", "name": "Abdominal Pain", "category": "Gastrointestinal", "is_red_flag": False, "description": "Pain or cramping anywhere in the tummy area."},
    {"code": "severe_abdominal_pain", "name": "Severe Abdominal Pain", "category": "Gastrointestinal", "is_red_flag": True, "description": "Intense, acute abdominal pain, potentially indicating surgical emergency."},
    {"code": "bloating", "name": "Bloating", "category": "Gastrointestinal", "is_red_flag": False, "description": "Feeling of fullness or swelling in the abdomen."},
    {"code": "heartburn", "name": "Heartburn / Acid Reflux", "category": "Gastrointestinal", "is_red_flag": False, "description": "Burning sensation in the chest or throat caused by stomach acid."},
    {"code": "loss_of_appetite", "name": "Loss of Appetite", "category": "Gastrointestinal", "is_red_flag": False, "description": "Reduced desire to eat."},
    {"code": "dysphagia", "name": "Difficulty Swallowing", "category": "Gastrointestinal", "is_red_flag": False, "description": "Sensation of food or liquid sticking in the throat or chest."},
    {"code": "melena", "name": "Black / Tarry Stool", "category": "Gastrointestinal", "is_red_flag": True, "description": "Dark, tarry feces, indicating upper gastrointestinal bleeding."},
    {"code": "hematochezia", "name": "Bright Red Blood in Stool", "category": "Gastrointestinal", "is_red_flag": True, "description": "Fresh blood in or with stool, indicating lower gastrointestinal bleeding."},
    {"code": "jaundice", "name": "Jaundice", "category": "Gastrointestinal", "is_red_flag": True, "description": "Yellowing of the skin and whites of the eyes, indicating liver dysfunction."},

    # --- Neurological ---
    {"code": "headache", "name": "Headache", "category": "Neurological", "is_red_flag": False, "description": "Pain in any part of the head."},
    {"code": "severe_headache", "name": "Sudden Severe Headache", "category": "Neurological", "is_red_flag": True, "description": "Sudden, excruciating headache ('thunderclap'), potential stroke or aneurysm sign."},
    {"code": "migraine", "name": "Migraine Pain", "category": "Neurological", "is_red_flag": False, "description": "Throbbing headache, often unilateral, with sensitivity to light and sound."},
    {"code": "numbness", "name": "Numbness / Loss of Sensation", "category": "Neurological", "is_red_flag": False, "description": "Lack of feeling in parts of the body."},
    {"code": "tingling", "name": "Tingling / Pins and Needles", "category": "Neurological", "is_red_flag": False, "description": "Prickling sensation, common in hands and feet."},
    {"code": "unilateral_weakness", "name": "One-sided Weakness", "category": "Neurological", "is_red_flag": True, "description": "Weakness or paralysis in one arm, leg, or side of face. Major stroke indicator."},
    {"code": "confusion", "name": "Confusion / Disorientation", "category": "Neurological", "is_red_flag": True, "description": "Inability to think clearly or know where one is."},
    {"code": "slurred_speech", "name": "Slurred Speech / Aphasia", "category": "Neurological", "is_red_flag": True, "description": "Difficulty speaking, slurring words, or trouble understanding language."},
    {"code": "seizures", "name": "Seizures / Convulsions", "category": "Neurological", "is_red_flag": True, "description": "Sudden, uncontrolled electrical disturbance in the brain."},
    {"code": "memory_loss", "name": "Short-term Memory Loss", "category": "Neurological", "is_red_flag": False, "description": "Difficulty remembering recent events or facts."},
    {"code": "tremor", "name": "Tremors / Shaking", "category": "Neurological", "is_red_flag": False, "description": "Involuntary, rhythmic muscle contraction and relaxation."},
    {"code": "loss_of_balance", "name": "Loss of Balance / Ataxia", "category": "Neurological", "is_red_flag": False, "description": "Difficulty walking straight or maintaining posture."},

    # --- Musculoskeletal ---
    {"code": "joint_pain", "name": "Joint Pain", "category": "Musculoskeletal", "is_red_flag": False, "description": "Pain or discomfort in one or more joints."},
    {"code": "joint_stiffness", "name": "Joint Stiffness", "category": "Musculoskeletal", "is_red_flag": False, "description": "Difficulty moving joints, especially in the morning."},
    {"code": "joint_swelling", "name": "Joint Swelling", "category": "Musculoskeletal", "is_red_flag": False, "description": "Accumulation of fluid around a joint."},
    {"code": "back_pain", "name": "Back Pain", "category": "Musculoskeletal", "is_red_flag": False, "description": "Ache or stiffness anywhere in the back."},
    {"code": "neck_pain", "name": "Neck Pain", "category": "Musculoskeletal", "is_red_flag": False, "description": "Pain or stiffness in the cervical spine area."},
    {"code": "muscle_pain", "name": "Muscle Pain / Myalgia", "category": "Musculoskeletal", "is_red_flag": False, "description": "Aching or sore muscles."},
    {"code": "muscle_cramps", "name": "Muscle Cramps", "category": "Musculoskeletal", "is_red_flag": False, "description": "Sudden, painful, involuntary contraction of muscles."},
    {"code": "bone_pain", "name": "Bone Pain", "category": "Musculoskeletal", "is_red_flag": False, "description": "Deep, boring pain in the bones."},
    {"code": "stiff_neck", "name": "Stiff Neck with Fever", "category": "Musculoskeletal", "is_red_flag": True, "description": "Inability to bend neck forward, associated with fever. Meningitis red flag."},

    # --- Dermatology ---
    {"code": "skin_rash", "name": "Skin Rash", "category": "Dermatology", "is_red_flag": False, "description": "Area of irritated or swollen skin."},
    {"code": "purpuric_rash", "name": "Non-blanching Rash / Purpura", "category": "Dermatology", "is_red_flag": True, "description": "Purple or red spots that do not fade when pressed. Sepsis/Meningitis sign."},
    {"code": "itching", "name": "Itching / Pruritus", "category": "Dermatology", "is_red_flag": False, "description": "An uncomfortable, irritating sensation that creates an urge to scratch."},
    {"code": "dry_skin", "name": "Dry Skin", "category": "Dermatology", "is_red_flag": False, "description": "Skin lacking moisture or oil, appearing flaky."},
    {"code": "skin_redness", "name": "Skin Redness / Erythema", "category": "Dermatology", "is_red_flag": False, "description": "Redness of skin, often indicating inflammation or infection."},
    {"code": "hives", "name": "Hives / Urticaria", "category": "Dermatology", "is_red_flag": False, "description": "Raised, red, itchy welts on the skin."},
    {"code": "skin_lesion", "name": "Atypical Skin Lesion / Mole", "category": "Dermatology", "is_red_flag": False, "description": "A mole or spot changing color, shape, or size."},
    {"code": "hair_loss", "name": "Hair Loss / Alopecia", "category": "Dermatology", "is_red_flag": False, "description": "Thinning hair or bald patches."},
    {"code": "brittle_nails", "name": "Brittle Nails", "category": "Dermatology", "is_red_flag": False, "description": "Nails that split, peel, or break easily."},

    # --- ENT & Ophthalmic ---
    {"code": "ear_pain", "name": "Ear Pain", "category": "ENT", "is_red_flag": False, "description": "Pain inside or behind the ear."},
    {"code": "tinnitus", "name": "Tinnitus (Ringing in Ears)", "category": "ENT", "is_red_flag": False, "description": "Hearing sounds in the ears when no external sound is present."},
    {"code": "hearing_loss", "name": "Hearing Loss", "category": "ENT", "is_red_flag": False, "description": "Partial or complete inability to hear sounds in one or both ears."},
    {"code": "nosebleed", "name": "Nosebleed / Epistaxis", "category": "ENT", "is_red_flag": False, "description": "Bleeding from the nose."},
    {"code": "sinus_pressure", "name": "Sinus Pressure", "category": "ENT", "is_red_flag": False, "description": "Pain or pressure around the eyes, cheeks, and forehead."},
    {"code": "hoarseness", "name": "Hoarseness / Voice Change", "category": "ENT", "is_red_flag": False, "description": "Abnormal voice changes, raspy or strained voice."},
    {"code": "vision_loss", "name": "Sudden Vision Loss", "category": "ENT", "is_red_flag": True, "description": "Sudden decrease or total loss of sight in one or both eyes."},
    {"code": "double_vision", "name": "Double Vision / Diplopia", "category": "ENT", "is_red_flag": True, "description": "Seeing two images of a single object."},
    {"code": "eye_pain", "name": "Eye Pain", "category": "ENT", "is_red_flag": False, "description": "Physical pain or soreness in or around the eye."},
    {"code": "photophobia", "name": "Sensitivity to Light / Photophobia", "category": "ENT", "is_red_flag": False, "description": "Discomfort or pain in the eyes when exposed to light."},

    # --- Urinary & Reproductive ---
    {"code": "burning_urination", "name": "Burning Urination / Dysuria", "category": "Urinary", "is_red_flag": False, "description": "Pain, discomfort, or burning sensation when passing urine."},
    {"code": "frequent_urination", "name": "Frequent Urination", "category": "Urinary", "is_red_flag": False, "description": "Needing to urinate more often than usual."},
    {"code": "urgent_urination", "name": "Urgent Urination", "category": "Urinary", "is_red_flag": False, "description": "Sudden, strong, compelling urge to urinate."},
    {"code": "hematuria", "name": "Blood in Urine", "category": "Urinary", "is_red_flag": True, "description": "Urine that is pink, red, or cola-colored due to red blood cells."},
    {"code": "anuria", "name": "Inability to Urinate / Anuria", "category": "Urinary", "is_red_flag": True, "description": "Failure of the kidneys to produce urine, or complete blockage."},
    {"code": "urinary_incontinence", "name": "Urinary Incontinence", "category": "Urinary", "is_red_flag": False, "description": "Loss of bladder control, leaking urine."},
    {"code": "pelvic_pain", "name": "Pelvic Pain", "category": "Urinary", "is_red_flag": False, "description": "Pain in the lowest part of the abdomen and pelvis."},
    {"code": "flank_pain", "name": "Flank Pain", "category": "Urinary", "is_red_flag": False, "description": "Pain on the side of the body between the upper abdomen and the back, often kidney-related."},

    # --- Mental & Psychological ---
    {"code": "anxiety", "name": "Anxiety / Nervousness", "category": "Mental Health", "is_red_flag": False, "description": "Feelings of worry, anxiety, or fear strong enough to interfere with daily activities."},
    {"code": "depression", "name": "Depression / Low Mood", "category": "Mental Health", "is_red_flag": False, "description": "Persistent feeling of sadness, emptiness, or loss of interest."},
    {"code": "mood_swings", "name": "Mood Swings", "category": "Mental Health", "is_red_flag": False, "description": "Rapid or extreme changes in mood."},
    {"code": "panic_attacks", "name": "Panic Attacks", "category": "Mental Health", "is_red_flag": False, "description": "Sudden episodes of intense fear, physical reactions (sweating, racing heart)."},
    {"code": "irritability", "name": "Irritability", "category": "Mental Health", "is_red_flag": False, "description": "Easy annoyance or impatience."},
    {"code": "lack_of_focus", "name": "Difficulty Concentrating", "category": "Mental Health", "is_red_flag": False, "description": "Trouble focusing thoughts or staying on task."},
    {"code": "suicidal_ideation", "name": "Suicidal Thoughts", "category": "Mental Health", "is_red_flag": True, "description": "Thoughts of self-harm or ending one's life."},

    # --- General / Constitutional ---
    {"code": "fever", "name": "Fever", "category": "General", "is_red_flag": False, "description": "Elevated body temperature above normal (typically > 37.8C or 100F)."},
    {"code": "high_fever", "name": "High Fever (>39.5C)", "category": "General", "is_red_flag": True, "description": "Very high body temperature requiring urgent cooling and diagnosis."},
    {"code": "fatigue", "name": "Fatigue / Extreme Tiredness", "category": "General", "is_red_flag": False, "description": "Persistent state of exhaustion or lack of energy."},
    {"code": "weakness", "name": "General Weakness / Lethargy", "category": "General", "is_red_flag": False, "description": "Lack of muscle strength, feeling sluggish."},
    {"code": "chills", "name": "Chills / Shivering", "category": "General", "is_red_flag": False, "description": "Cold sensation accompanied by shivering."},
    {"code": "night_sweats", "name": "Night Sweats", "category": "General", "is_red_flag": False, "description": "Drenching sweats during sleep, unrelated to bedroom temperature."},
    {"code": "weight_loss", "name": "Unexplained Weight Loss", "category": "General", "is_red_flag": False, "description": "Losing weight without trying, dieting, or exercising."},
    {"code": "weight_gain", "name": "Unexplained Weight Gain", "category": "General", "is_red_flag": False, "description": "Gaining weight rapidly without a change in diet or activity."},
    {"code": "insomnia", "name": "Insomnia", "category": "General", "is_red_flag": False, "description": "Difficulty falling or staying asleep."},
    {"code": "excessive_sleep", "name": "Hypersomnia", "category": "General", "is_red_flag": False, "description": "Sleeping excessively or feeling sleepy during the day."},
    {"code": "body_pain", "name": "Generalized Body Ache", "category": "General", "is_red_flag": False, "description": "Aching feeling throughout the muscles and joints of the body."},
    {"code": "polydipsia", "name": "Excessive Thirst", "category": "General", "is_red_flag": False, "description": "Feeling thirsty all the time, classic diabetes symptom."},
    {"code": "polyphagia", "name": "Excessive Hunger", "category": "General", "is_red_flag": False, "description": "Increased appetite and food intake, classic diabetes symptom."},
    {"code": "polyuria", "name": "Excessive Urination", "category": "General", "is_red_flag": False, "description": "Passing abnormally large volumes of urine, classic diabetes symptom."},
    {"code": "slow_healing_sores", "name": "Slow-healing Sores", "category": "General", "is_red_flag": False, "description": "Cuts or bruises that take an unusually long time to heal."}
]

def seed_symptoms():
    db = SessionLocal()
    try:
        # Check if symptoms already seeded
        count = db.query(Symptom).count()
        if count > 0:
            print(f"Symptoms table already seeded with {count} symptoms.")
            return

        print("Seeding symptoms...")
        for index, item in enumerate(SYMPTOMS_LIST):
            symptom = Symptom(
                id=index + 1,
                code=item["code"],
                name=item["name"],
                category=item["category"],
                is_red_flag=item["is_red_flag"],
                description=item.get("description", "")
            )
            db.add(symptom)
        db.commit()
        print("Symptoms successfully seeded.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding symptoms: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_symptoms()
