"""
labels.py: Localized UI copy and text labels for LoadShare / Routeway landing page.

Centralized dictionary for bilingual text strings (English and Hindi).
This will later be migrated to database configurations.
"""

LANDING_PAGE_LABELS = {
    # Brand Identity
    "brand_name": {"en": "ROUTEWAY", "hi": "लोडशेयर"},
    "brand_tagline": {
        "en": "Direct Corridor Freight & Parcel Delivery",
        "hi": "डायरेक्ट कॉरिडोर फ्रेट और पार्सल डिलीवरी",
    },
    "pilot_notice": {
        "en": "PILOT PHASE: Commercial Senders Only on Delhi ⇄ Jaipur Corridor",
        "hi": "पायलट चरण: केवल दिल्ली ⇄ जयपुर कॉरिडोर हेतु पार्सल सेवा",
    },
    # Hero Section
    "hero_headline": {
        "en": "Send parcels on trucks already traveling your route",
        "hi": "उसी रूट पर जा रहे ट्रकों से किफायती पार्सल भेजें",
    },
    "hero_subtitle": {
        "en": "Direct Delhi ⇄ Jaipur delivery at wholesale rates — no hub-handling, no middlemen.",
        "hi": "सीधा दिल्ली ⇄ जयपुर डिलीवरी थोक दरों पर — बिना किसी बिचौलिए या अतिरिक्त हैंडलिंग के।",
    },
    "btn_book_delivery": {
        "en": "Book a delivery",
        "hi": "डिलीवरी बुक करें",
    },
    "btn_see_rates": {
        "en": "See rates",
        "hi": "दरें देखें",
    },
    # Tracker Preview & State Switcher
    "tracker_preview": {
        "en": "Tracker Preview",
        "hi": "ट्रैकर पूर्वावलोकन",
    },
    "btn_item_in_dispatch": {
        "en": "Item in dispatch",
        "hi": "डिस्पैच में पार्सल",
    },
    "btn_loading_state": {
        "en": "Loading",
        "hi": "लोडिंग",
    },
    "btn_empty_state": {
        "en": "No item in dispatch",
        "hi": "कोई डिस्पैच नहीं",
    },
    "dispatch_status": {
        "en": "Current Item for dispatch",
        "hi": "वर्तमान आइटम डिस्पैच में",
    },
    "dispatch_transit": {
        "en": "8H TRANSIT",
        "hi": "8 घंटे ट्रांजिट",
    },
    "origin_hub_title": {
        "en": "ORIGIN HUB",
        "hi": "उत्पत्ति हब",
    },
    "origin_city": {
        "en": "Delhi",
        "hi": "दिल्ली",
    },
    "origin_hub_name": {
        "en": "Sanjay Gandhi Hub",
        "hi": "संजय गांधी हब",
    },
    "corridor_badge": {
        "en": "NH48 EXPRESS",
        "hi": "NH48 एक्सप्रेस",
    },
    "destination_hub_title": {
        "en": "DESTINATION",
        "hi": "गंतव्य हब",
    },
    "destination_city": {
        "en": "Jaipur",
        "hi": "जयपुर",
    },
    "destination_hub_name": {
        "en": "VKI Industrial Area",
        "hi": "VKI इंडस्ट्रियल एरिया",
    },
    "departs_label": {
        "en": "Departs daily at",
        "hi": "दैनिक रवानगी",
    },
    "arrival_label": {
        "en": "Arrival at",
        "hi": "पहुंचने का समय",
    },
    "departure_time": {
        "en": "20:30",
        "hi": "20:30",
    },
    "arrival_time": {
        "en": "05:30",
        "hi": "05:30",
    },
    "empty_dispatch_title": {
        "en": "No active shipments currently in dispatch",
        "hi": "वर्तमान में कोई सक्रिय शिपमेंट डिस्पैच में नहीं है",
    },
    "empty_dispatch_desc": {
        "en": "There are currently no parcels booked on tonight's corridor transit. Secure capacity now before cut-off.",
        "hi": "आज रात के कॉरिडोर ट्रांजिट के लिए कोई पार्सल बुक नहीं है। कट-ऑफ समय से पहले स्थान सुरक्षित करें।",
    },
    "btn_book_parcel": {
        "en": "Book a parcel",
        "hi": "पार्सल बुक करें",
    },
    # Transit Guarantees & Safety Protocol
    "transit_guarantees_title": {
        "en": "Transit Guarantees & Safety Protocol",
        "hi": "ट्रांजिट गारंटी और सुरक्षा प्रोटोकॉल",
    },
    "guarantee_1_title": {
        "en": "OTP at pickup",
        "hi": "पिकअप पर OTP",
    },
    "guarantee_1_desc": {
        "en": "Sender auth pin",
        "hi": "प्रेषक सत्यापन पिन",
    },
    "guarantee_2_title": {
        "en": "OTP at drop",
        "hi": "ड्रॉप पर OTP",
    },
    "guarantee_2_desc": {
        "en": "Receiver unlock pin",
        "hi": "प्राप्तकर्ता अनलॉक पिन",
    },
    "guarantee_3_title": {
        "en": "Verified drivers",
        "hi": "सत्यापित चालक",
    },
    "guarantee_3_desc": {
        "en": "KYC & DL audited",
        "hi": "KYC और DL ऑडिटेड",
    },
    "guarantee_4_title": {
        "en": "Live alerts",
        "hi": "लाइव अलर्ट",
    },
    "guarantee_4_desc": {
        "en": "Toll & checkpoint SMS",
        "hi": "टोल और चेकपॉइंट SMS",
    },
    # How It Works
    "how_it_works_title": {
        "en": "How it works",
        "hi": "यह कैसे काम करता है",
    },
    "how_it_works_subtitle": {
        "en": "Simple 3-step logistics direct on existing highway transit.",
        "hi": "मौजूदा हाईवे ट्रांजिट पर सीधा 3-चरण लॉजिस्टिक्स।",
    },
    "step_1_num": {"en": "01", "hi": "01"},
    "step_1_title": {
        "en": "Request",
        "hi": "अनुरोध करें",
    },
    "step_1_desc": {
        "en": "Specify parcel weight and pickup hub along NH48.",
        "hi": "NH48 पर पार्सल वजन और पिकअप हब चुनें।",
    },
    "step_2_num": {"en": "02", "hi": "02"},
    "step_2_title": {
        "en": "Match",
        "hi": "मिलान",
    },
    "step_2_desc": {
        "en": "Paired with a verified commercial truck scheduled for tonight.",
        "hi": "आज रात रवाना होने वाले सत्यापित ट्रक से मिलान।",
    },
    "step_3_num": {"en": "03", "hi": "03"},
    "step_3_title": {
        "en": "Track & receive",
        "hi": "ट्रैक करें और प्राप्त करें",
    },
    "step_3_desc": {
        "en": "Secured handover via OTP verification at pickup and drop.",
        "hi": "पिकअप और डिलीवरी पर OTP सत्यापन के साथ सुरक्षित हैंडओवर।",
    },
    # Collapsible FAQs
    "faq_title": {
        "en": "Frequently asked questions",
        "hi": "अक्सर पूछे जाने वाले प्रश्न",
    },
    "faq_subtitle": {
        "en": "Direct answers about shipping along the corridor.",
        "hi": "कॉरिडोर पर पार्सल भेजने से जुड़े सीधे उत्तर।",
    },
    "faq_1_q": {
        "en": "1. What items are prohibited from transport?",
        "hi": "1. किन वस्तुओं का परिवहन वर्जित है?",
    },
    "faq_1_a": {
        "en": "Flammable liquids, hazardous chemicals, firearms, unpackaged glassware, illegal narcotics, and unmanifested perishable food items are strictly prohibited under Motor Vehicles carriage regulations.",
        "hi": "मोटर वाहन नियमों के तहत ज्वलनशील तरल पदार्थ, खतरनाक रसायन, हथियार, बिना पैक कांच का सामान और अवैध वस्तुएं पूरी तरह से वर्जित हैं।",
    },
    "faq_2_q": {
        "en": "2. What payment methods are supported?",
        "hi": "2. कौन से भुगतान विकल्प उपलब्ध हैं?",
    },
    "faq_2_a": {
        "en": "We operate strictly on Pay On Delivery (POD). The consignee or sender can settle via instant UPI QR scan upon OTP handover, or through cash at the depot counter.",
        "hi": "हम पूरी तरह से Pay On Delivery (POD) पर काम करते हैं। OTP सत्यापन के समय UPI QR स्कैन या डिपो काउंटर पर नकद भुगतान करें।",
    },
    "faq_3_q": {
        "en": "3. How is the final rate calculated and locked?",
        "hi": "3. अंतिम दर कैसे तय और लॉक की जाती है?",
    },
    "faq_3_a": {
        "en": "Rates are calculated purely on actual deadweight measured at the hub scale. Once your booking OTP is generated, your per-kilogram rate bracket is locked and immune to transit surcharges.",
        "hi": "दरें केवल हब कांटे पर मापे गए वास्तविक वजन पर आधारित होती हैं। एक बार बुकिंग OTP बनने के बाद प्रति-किलो दर तय हो जाती है।",
    },
    "faq_4_q": {
        "en": "4. Where are the pickup windows and storage hubs?",
        "hi": "4. पिकअप और स्टोरेज हब कहां स्थित हैं?",
    },
    "faq_4_a": {
        "en": "Delhi cargo is received at Sanjay Gandhi Transport Nagar (Bay 4). Jaipur cargo is made available for collection at VKI Depot from 06:00 AM. Free secure depot storage is provided for up to 24 hours.",
        "hi": "दिल्ली का माल संजय गांधी ट्रांसपोर्ट नगर में लिया जाता है। जयपुर में माल सुबह 06:00 बजे से VKI डिपो पर 24 घंटे की मुफ्त सुरक्षित स्टोरेज के साथ उपलब्ध रहता है।",
    },
    # Clean Footer
    "footer_brand_desc": {
        "en": "Direct highway transit for businesses, manufacturers, and trade consignments.",
        "hi": "व्यापारियों और निर्माताओं के लिए सीधा हाईवे फ्रेट ट्रांजिट।",
    },
    "footer_helpline_label": {
        "en": "Concierge Dispatch Helpline",
        "hi": "डिस्पैच हेल्पलाइन",
    },
    "footer_helpline_phone": {
        "en": "1800-419-7688",
        "hi": "1800-419-7688",
    },
    "footer_support_label": {
        "en": "Operational Support",
        "hi": "परिचालन सहायता",
    },
    "footer_whatsapp": {
        "en": "WhatsApp Operations Desk",
        "hi": "व्हाट्सएप ऑपरेशंस डेस्क",
    },
    "footer_driver_app": {
        "en": "Commercial Drivers Android App (APK)",
        "hi": "कमर्शियल ड्राइवर्स एंड्रॉइड ऐप (APK)",
    },
    "footer_copyright": {
        "en": "© 2025 Routeway Logistics India Ltd. All rights reserved.",
        "hi": "© 2025 रूटवे लॉजिस्टिक्स इंडिया लिमिटेड। सर्वाधिकार सुरक्षित।",
    },
    "footer_legal": {
        "en": "Registered inter-city common parcel carrier. Operations comply strictly with the Carriage by Road Act, 2007 and Central Motor Vehicles Rules.",
        "hi": "सड़क परिवहन अधिनियम, 2007 एवं केंद्रीय मोटर वाहन नियमों के तहत पंजीकृत इंटर-सिटी पार्सल कैरियर।",
    },
    # Subviews (Tabs) Placeholders
    "rates_title": {
        "en": "Wholesale Corridor Rates",
        "hi": "थोक कॉरिडोर दरें",
    },
    "rates_subtitle": {
        "en": "Wholesale per-kg corridor pricing starting at ₹6.00/kg for part-loads.",
        "hi": "पार्ट-लोड के लिए थोक प्रति-किग्रा दरें ₹6.00/किग्रा से शुरू।",
    },
    "support_title": {
        "en": "24x7 Corridor Helpline & Concierge",
        "hi": "24x7 कॉरिडोर हेल्पलाइन एवं कंसीयर्ज",
    },
    "support_subtitle": {
        "en": "Direct phone support, WhatsApp dispatch tracking, and live depot concierge services.",
        "hi": "सीधा फोन सपोर्ट, व्हाट्सएप ट्रैकिंग और डिपो कंसीयर्ज सेवाएं।",
    },
    "profile_title": {
        "en": "Sender Business Profile",
        "hi": "प्रेषक व्यवसाय प्रोफाइल",
    },
    "profile_subtitle": {
        "en": "Manage business GSTIN, saved pickup/drop hubs, and consignment history.",
        "hi": "व्यवसाय GSTIN, सहेजे गए पिकअप/ड्रॉप हब और कंसाइनमेंट विवरण प्रबंधित करें।",
    },
    # Navigation Items
    "nav_book": {"en": "Book", "hi": "बुक करें"},
    "nav_rates": {"en": "Rates", "hi": "दरें"},
    "nav_home": {"en": "Home", "hi": "होम"},
    "nav_support": {"en": "Support", "hi": "सहायता"},
    "nav_profile": {"en": "Profile", "hi": "प्रोफ़ाइल"},
}
