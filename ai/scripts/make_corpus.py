"""Generate the SYNTHETIC deal-memo corpus used by the RAG demo.

Every company, person and number below is fictional and was written by hand
for this project. Any resemblance to real companies is coincidental.
Half of the memos are in Vietnamese, half in English, and several companies
deliberately look alike (e.g. four payment startups) so that retrieval has
realistic distractors.

Run:  python scripts/make_corpus.py   (writes data/corpus/*.md)
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "corpus"

HEADINGS = {
    "vi": [
        "Tổng quan",
        "Đội ngũ",
        "Sản phẩm",
        "Mô hình kinh doanh",
        "Số liệu tăng trưởng",
        "Gọi vốn",
        "Rủi ro",
    ],
    "en": ["Overview", "Team", "Product", "Business model", "Traction", "Fundraising", "Risks"],
}

MEMOS: list[dict] = [
    # ---------------- Fintech / payments (distractor cluster) ----------------
    {
        "id": "paynest",
        "name": "PayNest",
        "lang": "en",
        "sections": [
            "PayNest is a Ho Chi Minh City startup founded in 2023 that offers QR payment acceptance for street-food vendors and small kiosks. Stage: Seed. Pipeline status: Due Diligence.",
            "CEO Tran Minh Khoa previously led merchant onboarding at a regional e-wallet for four years. CTO Le Thu Ha was a backend engineer at a core-banking vendor. The team has 18 full-time employees.",
            "Vendors print a static VietQR code; payments settle to the vendor's bank account the next business day. A lightweight Android app shows daily sales and sends a voice alert for every payment received.",
            "PayNest charges merchants nothing for acceptance and earns a 0.3% fee on instant settlement, which 22% of merchants choose. It also earns referral fees from partner banks for each micro-loan originated.",
            "As of September 2026 PayNest has 41,000 active merchants and monthly payment volume (TPV) of 96 billion VND, growing 14% month over month. Merchant churn after 90 days is 9%.",
            "PayNest is raising a 2.5 million USD Seed round at an 11 million USD pre-money valuation. Funds go to merchant acquisition in Da Nang and Can Tho and to a fraud-monitoring team.",
            "Key risks: thin take rate, dependence on one partner bank for settlement, and aggressive competition from large e-wallets that subsidise merchant acquisition.",
        ],
    },
    {
        "id": "vixanh",
        "name": "VíXanh",
        "lang": "vi",
        "sections": [
            "VíXanh là startup ví điện tử dành cho học sinh, sinh viên tại Hà Nội, thành lập năm 2022. Giai đoạn: Series A. Trạng thái pipeline: Reviewing.",
            "Nhà sáng lập Nguyễn Hoàng Lan từng là quản lý sản phẩm tại một ngân hàng số trong 5 năm. Đồng sáng lập Phạm Đức Anh phụ trách công nghệ, từng làm kỹ sư bảo mật. Công ty có 35 nhân sự.",
            "Ứng dụng cho phép phụ huynh nạp tiền tiêu vặt, đặt hạn mức chi tiêu theo ngày và theo dõi giao dịch của con theo thời gian thực. Học sinh thanh toán ở căng tin trường bằng mã QR.",
            "VíXanh thu phí 1,2% trên mỗi giao dịch từ các căng tin đối tác và bán gói quản lý chi tiêu cao cấp cho phụ huynh với giá 29.000 đồng mỗi tháng.",
            "Tính đến tháng 8 năm 2026, VíXanh có 260.000 người dùng đã xác thực eKYC và hợp tác với 410 trường học. Doanh thu tháng đạt 1,8 tỷ đồng.",
            "VíXanh đang gọi vòng Series A 6 triệu USD, định giá trước vốn 30 triệu USD, để mở rộng vào TP. Hồ Chí Minh và xin giấy phép trung gian thanh toán riêng.",
            "Rủi ro chính: ví hiện hoạt động nhờ giấy phép của đối tác, quy định về tài khoản trẻ vị thành niên có thể thay đổi, và tỷ lệ sử dụng giảm mạnh trong kỳ nghỉ hè.",
        ],
    },
    {
        "id": "tiennhanh",
        "name": "Tiền Nhanh",
        "lang": "vi",
        "sections": [
            "Tiền Nhanh là nền tảng chuyển tiền kiều hối từ Hàn Quốc và Nhật Bản về Việt Nam, thành lập năm 2021 tại Đà Nẵng. Giai đoạn: Seed. Trạng thái pipeline: New.",
            "CEO Võ Thị Mai từng làm 6 năm tại bộ phận kiều hối của một ngân hàng thương mại. Đội ngũ gồm 14 người, trong đó 5 người làm tuân thủ và chống rửa tiền.",
            "Người lao động ở nước ngoài chuyển tiền qua ứng dụng, người nhận tại Việt Nam nhận vào tài khoản ngân hàng hoặc ví điện tử trong vòng 10 phút.",
            "Tiền Nhanh thu phí cố định 3 USD mỗi giao dịch cộng chênh lệch tỷ giá khoảng 0,8%.",
            "Năm 2026 Tiền Nhanh xử lý trung bình 38.000 giao dịch mỗi tháng, giá trị trung bình 520 USD mỗi giao dịch. 63% khách hàng chuyển tiền lặp lại hằng tháng.",
            "Công ty đang gọi vốn 1,5 triệu USD vòng Seed để xin thêm giấy phép tại Đài Loan.",
            "Rủi ro: phụ thuộc vào đối tác ngân hàng đại lý ở nước ngoài, biến động tỷ giá, và chi phí tuân thủ chống rửa tiền cao.",
        ],
    },
    {
        "id": "ledgerly",
        "name": "Ledgerly",
        "lang": "en",
        "sections": [
            "Ledgerly is a Hanoi-based SaaS startup founded in 2024 that automates bookkeeping and e-invoice reconciliation for SMEs. Stage: Pre-Seed. Pipeline status: Reviewing.",
            "Founder Dang Quoc Bao is a former auditor at a Big Four firm. Co-founder Hoang Mai Linh built OCR products at a document-processing startup. The team has 9 people.",
            "Ledgerly connects to bank accounts and to the national e-invoice system, uses OCR to read supplier invoices, and suggests matching journal entries that an accountant approves with one click.",
            "Subscription pricing: 499,000 VND per month for up to 300 invoices, 1,490,000 VND per month for unlimited invoices.",
            "Ledgerly has 620 paying SMEs and annual recurring revenue (ARR) of 210,000 USD. Net revenue retention is 118%.",
            "Ledgerly is raising 800,000 USD at a 5 million USD post-money valuation.",
            "Risks: OCR accuracy on handwritten receipts is only about 81%, and accounting-software incumbents may bundle a similar feature.",
        ],
    },
    # ---------------- Lending ----------------
    {
        "id": "sokalend",
        "name": "SoKa Lend",
        "lang": "en",
        "sections": [
            "SoKa Lend provides invoice financing for suppliers of large retail chains. Founded in 2022 in Ho Chi Minh City. Stage: Series A. Pipeline status: Due Diligence.",
            "CEO Bui Thanh Tung spent 8 years in corporate credit at a commercial bank. Chief Risk Officer Ngo Phuong Thao built credit scorecards at a consumer-finance company. 27 employees.",
            "Suppliers upload approved invoices; SoKa Lend advances 85% of the invoice value within 24 hours and collects payment directly from the retailer at maturity.",
            "SoKa Lend earns a discount fee of 1.4% per 30 days on the advanced amount and funds loans through a credit line from two local banks.",
            "Cumulative disbursement reached 1,350 billion VND by October 2026. The 30-day non-performing loan (NPL) ratio is 1.1%. Average invoice tenor is 47 days.",
            "SoKa Lend is raising 8 million USD in equity plus a 20 million USD debt facility.",
            "Risks: concentration, because the top three retailers account for 58% of receivables, plus rising funding costs if interest rates go up.",
        ],
    },
    {
        "id": "vaynongdan",
        "name": "Vay Nông Dân",
        "lang": "vi",
        "sections": [
            "Vay Nông Dân cung cấp khoản vay vi mô mua vật tư nông nghiệp cho nông dân trồng lúa ở Đồng bằng sông Cửu Long. Thành lập năm 2023 tại Cần Thơ. Giai đoạn: Pre-Seed. Trạng thái pipeline: New.",
            "Nhà sáng lập Lê Văn Phúc lớn lên trong gia đình trồng lúa và từng làm chuyên viên tín dụng tại một quỹ tín dụng nhân dân. Đội ngũ có 11 người.",
            "Nông dân đăng ký qua đại lý vật tư; khoản vay được giải ngân trực tiếp cho đại lý dưới dạng phân bón và giống, nông dân trả nợ sau vụ thu hoạch.",
            "Công ty thu lãi 1,5% mỗi tháng và nhận hoa hồng 2% từ đại lý vật tư.",
            "Đã giải ngân cho 3.200 hộ nông dân với tổng dư nợ 42 tỷ đồng. Tỷ lệ nợ quá hạn trên 90 ngày là 3,4%, chủ yếu do vụ hè thu năm 2025 mất mùa.",
            "Đang gọi vốn 700.000 USD để xây dựng mô hình chấm điểm tín dụng dựa trên ảnh vệ tinh.",
            "Rủi ro: thời tiết và giá lúa ảnh hưởng trực tiếp đến khả năng trả nợ; quy định về lãi suất cho vay có thể siết chặt.",
        ],
    },
    {
        "id": "creditbee",
        "name": "CreditBee",
        "lang": "en",
        "sections": [
            "CreditBee offers buy-now-pay-later (BNPL) at electronics and phone retailers. Founded in 2021 in Hanoi. Stage: Series A. Pipeline status: Passed.",
            "CEO Nguyen Tuan Kiet was head of growth at a consumer-finance company. The team has 52 people, including a 9-person data science team.",
            "Shoppers split purchases into 3, 6 or 9 monthly installments at checkout after a two-minute approval based on eKYC and phone-usage data.",
            "Merchants pay CreditBee a 4% fee; consumers pay 0% interest on 3-month plans and 1.9% per month on longer plans.",
            "CreditBee has 1.1 million approved users and gross merchandise value (GMV) of 410 billion VND per month. The 90-day delinquency rate rose from 2.1% to 4.6% over the past year.",
            "CreditBee asked for 15 million USD. The fund passed because of the deteriorating delinquency trend and unclear unit economics.",
            "Risks: credit losses in a downturn, tightening BNPL regulation, and dependence on a few large electronics chains.",
        ],
    },
    # ---------------- Agritech ----------------
    {
        "id": "agriloop",
        "name": "AgriLoop",
        "lang": "en",
        "sections": [
            "AgriLoop turns rice straw and husk into organic fertiliser and biochar. Founded in 2022 in An Giang. Stage: Seed. Pipeline status: Reviewing.",
            "Founder Truong Ngoc Han holds a PhD in soil science; COO Phan Van Loc ran a fertiliser distributor for ten years. 23 employees, including 12 factory staff.",
            "AgriLoop collects straw that farmers would otherwise burn, composts it at a 5,000-tonne-per-year plant, and sells bagged fertiliser through agricultural cooperatives.",
            "Revenue comes from fertiliser sales (about 80%) and from carbon credits for avoided straw burning (about 20%).",
            "AgriLoop sold 3,100 tonnes of fertiliser in 2025, with revenue of 9.6 billion VND and a gross margin of 31%.",
            "AgriLoop is raising 3 million USD to build a second plant in Dong Thap.",
            "Risks: carbon-credit prices are volatile, and collection logistics are seasonal.",
        ],
    },
    {
        "id": "mekongfresh",
        "name": "MekongFresh",
        "lang": "vi",
        "sections": [
            "MekongFresh là sàn B2B kết nối hợp tác xã trái cây ở Tiền Giang với chuỗi siêu thị và nhà hàng tại TP. Hồ Chí Minh. Thành lập năm 2023. Giai đoạn: Seed. Trạng thái pipeline: Due Diligence.",
            "CEO Đỗ Thanh Trúc từng là trưởng bộ phận thu mua của một chuỗi siêu thị. CTO Huỳnh Gia Bảo xây dựng hệ thống quản lý kho lạnh. Đội ngũ 30 người.",
            "Người mua đặt hàng trước 18 giờ, MekongFresh gom hàng từ hợp tác xã, phân loại tại kho lạnh ở Mỹ Tho và giao trước 6 giờ sáng hôm sau.",
            "MekongFresh hưởng biên lợi nhuận khoảng 12% trên giá trị đơn hàng và thu phí dịch vụ kho lạnh.",
            "Giá trị đơn hàng (GMV) đạt 7,5 tỷ đồng mỗi tháng với 180 khách hàng doanh nghiệp. Tỷ lệ hàng hư hỏng giảm từ 9% xuống 3,5% sau khi dùng kho lạnh.",
            "Công ty đang gọi 2 triệu USD vòng Seed, định giá trước vốn 9 triệu USD.",
            "Rủi ro: biên lợi nhuận mỏng, khách hàng có thể mua trực tiếp từ hợp tác xã, và chi phí điện cho kho lạnh tăng.",
        ],
    },
    {
        "id": "nongtrai360",
        "name": "NôngTrại360",
        "lang": "vi",
        "sections": [
            "NôngTrại360 cung cấp cảm biến IoT và ứng dụng tư vấn tưới tiêu cho vườn sầu riêng. Thành lập năm 2024 tại Đắk Lắk. Giai đoạn: Pre-Seed. Trạng thái pipeline: New.",
            "Nhà sáng lập Y Moan Niê là kỹ sư điện tử, từng làm tại một công ty thiết bị đo lường. Đội ngũ 7 người.",
            "Cảm biến đo độ ẩm đất và nhiệt độ, gửi dữ liệu qua mạng LoRa; ứng dụng khuyến nghị lịch tưới và cảnh báo nguy cơ sốc nước trước mùa ra hoa.",
            "Bán bộ cảm biến với giá 4,5 triệu đồng và thu phí thuê bao 150.000 đồng mỗi tháng cho mỗi vườn.",
            "Có 540 vườn đang sử dụng; các vườn thử nghiệm tiết kiệm trung bình 27% lượng nước tưới.",
            "Đang gọi vốn 400.000 USD.",
            "Rủi ro: chi phí phần cứng cao so với thu nhập nông hộ, và giá sầu riêng biến động mạnh theo thị trường xuất khẩu.",
        ],
    },
    # ---------------- Edtech ----------------
    {
        "id": "hocvui",
        "name": "HọcVui",
        "lang": "vi",
        "sections": [
            "HọcVui là ứng dụng luyện toán theo chương trình phổ thông cho học sinh lớp 1 đến lớp 9. Thành lập năm 2021 tại Hà Nội. Giai đoạn: Series A. Trạng thái pipeline: Reviewing.",
            "CEO Trịnh Thu Trang từng là giáo viên toán 8 năm. CTO Lý Minh Quân từng làm kỹ sư học máy. Công ty có 46 nhân sự, trong đó 15 người biên soạn nội dung.",
            "Ứng dụng có hơn 12.000 bài tập, tự điều chỉnh độ khó theo năng lực của từng học sinh, và gửi báo cáo tiến độ hằng tuần cho phụ huynh.",
            "Mô hình freemium: gói trả phí 99.000 đồng mỗi tháng hoặc 790.000 đồng mỗi năm.",
            "Có 1,4 triệu người dùng đăng ký, 92.000 thuê bao trả phí; tỷ lệ chuyển đổi sang trả phí là 6,6%. Doanh thu năm 2025 đạt 48 tỷ đồng.",
            "HọcVui đang gọi 5 triệu USD vòng Series A để mở rộng sang môn tiếng Anh.",
            "Rủi ro: tính mùa vụ theo năm học, cạnh tranh từ ứng dụng miễn phí, và chi phí marketing tăng.",
        ],
    },
    {
        "id": "skillbridge",
        "name": "SkillBridge",
        "lang": "en",
        "sections": [
            "SkillBridge runs 12-week bootcamps that retrain factory workers as junior QA testers and IT support staff. Founded in 2023 in Binh Duong. Stage: Seed. Pipeline status: New.",
            "Founder Ha Quang Vinh managed training programmes at an electronics manufacturer. The team has 16 people, including 8 instructors.",
            "Courses run in the evening, combine online lessons with weekend labs, and end with a placement interview at partner employers.",
            "Students pay nothing upfront; SkillBridge receives 15% of the graduate's salary for 18 months (an income-share agreement), and employers pay a placement fee.",
            "So far 640 students have graduated, with a 74% job placement rate within three months.",
            "SkillBridge is raising 1.2 million USD.",
            "Risks: income-share agreements have uncertain legal status in Vietnam, and placement rates depend on the IT hiring market.",
        ],
    },
    # ---------------- Healthtech ----------------
    {
        "id": "carelink",
        "name": "CareLink",
        "lang": "en",
        "sections": [
            "CareLink is a telemedicine and home-nursing platform for elderly patients with chronic conditions. Founded in 2022 in Ho Chi Minh City. Stage: Seed. Pipeline status: Due Diligence.",
            "CEO Dr. Vu Hai Yen is a cardiologist with 12 years of hospital experience. The team has 21 staff plus a network of 140 freelance nurses.",
            "Families book video consultations and home nursing visits; nurses record blood pressure and blood glucose readings in the app, which alerts the doctor when readings are out of range.",
            "CareLink sells monthly care packages from 1.2 million VND and takes a 20% commission on nursing visits.",
            "CareLink serves 5,800 patients, with 2,300 on monthly packages. Monthly revenue is 2.9 billion VND and 30-day hospital readmission among package patients is 6%.",
            "CareLink is raising 2 million USD at a 10 million USD pre-money valuation.",
            "Risks: telemedicine regulation is still evolving, nurse quality control is hard at scale, and patient data must comply with the personal-data protection decree.",
        ],
    },
    {
        "id": "thuocre",
        "name": "ThuốcRẻ",
        "lang": "vi",
        "sections": [
            "ThuốcRẻ là nền tảng đặt thuốc theo đơn và giao tận nhà, liên kết với các nhà thuốc độc lập. Thành lập năm 2023 tại Hải Phòng. Giai đoạn: Pre-Seed. Trạng thái pipeline: Passed.",
            "Nhà sáng lập Đinh Văn Hùng là dược sĩ, từng quản lý một chuỗi 20 nhà thuốc. Đội ngũ 10 người.",
            "Người dùng chụp ảnh đơn thuốc, dược sĩ xác nhận đơn và nhà thuốc gần nhất giao hàng trong vòng 2 giờ.",
            "ThuốcRẻ thu hoa hồng 8% trên mỗi đơn hàng từ nhà thuốc.",
            "Đã liên kết với 150 nhà thuốc, có 9.000 đơn hàng mỗi tháng.",
            "Công ty xin 500.000 USD. Quỹ đã từ chối vì quy định về bán thuốc kê đơn trực tuyến chưa rõ ràng và biên lợi nhuận thấp.",
            "Rủi ro: pháp lý về bán thuốc trực tuyến, và các chuỗi nhà thuốc lớn tự xây dựng kênh giao hàng.",
        ],
    },
    # ---------------- Logistics ----------------
    {
        "id": "shipnhanh",
        "name": "ShipNhanh",
        "lang": "vi",
        "sections": [
            "ShipNhanh là dịch vụ giao hàng chặng cuối trong ngày cho người bán hàng online ở các tỉnh miền Trung. Thành lập năm 2022 tại Huế. Giai đoạn: Seed. Trạng thái pipeline: Reviewing.",
            "CEO Hồ Ngọc Sơn từng làm quản lý vận hành tại một công ty chuyển phát nhanh 7 năm. Đội ngũ văn phòng 25 người cùng 600 tài xế đối tác.",
            "Người bán tạo đơn qua ứng dụng hoặc tích hợp API với các sàn thương mại điện tử; thuật toán gom đơn theo tuyến giúp tài xế giao trung bình 45 đơn mỗi ngày.",
            "Phí giao hàng trung bình 18.000 đồng mỗi đơn, cộng phí thu hộ tiền mặt (COD) 0,5%.",
            "ShipNhanh giao 310.000 đơn mỗi tháng tại 5 tỉnh, tỷ lệ giao thành công lần đầu là 91%.",
            "Đang gọi 3 triệu USD vòng Seed để mở thêm 3 kho trung chuyển.",
            "Rủi ro: cạnh tranh giá với các hãng vận chuyển lớn, và tỷ lệ hoàn hàng COD cao vào mùa mưa bão.",
        ],
    },
    {
        "id": "coldchainvn",
        "name": "ColdChain VN",
        "lang": "en",
        "sections": [
            "ColdChain VN operates refrigerated trucks and a temperature-monitoring platform for seafood and pharmaceutical shippers. Founded in 2021 in Hai Phong. Stage: Series A. Pipeline status: Reviewing.",
            "CEO Mac Thi Huong was a regional director at a global freight forwarder. The team has 140 employees, including 95 drivers.",
            "Each truck carries IoT temperature loggers; shippers see live temperature on a dashboard and receive a compliance report for every trip.",
            "ColdChain VN charges per trip plus a 5% premium for pharmaceutical-grade monitoring.",
            "The fleet has 70 trucks. Annual revenue in 2025 was 6.2 million USD with an EBITDA margin of 9%. Temperature excursions occurred on 0.4% of trips.",
            "ColdChain VN is raising 10 million USD, half for new trucks and half for working capital.",
            "Risks: high capital intensity, fuel-price exposure, and customer concentration in seafood exporters.",
        ],
    },
    # ---------------- Proptech ----------------
    {
        "id": "nhatro",
        "name": "NhàTrọ+",
        "lang": "vi",
        "sections": [
            "NhàTrọ+ là phần mềm quản lý phòng trọ cho chủ nhà cho thuê ở các khu công nghiệp. Thành lập năm 2024 tại Bắc Ninh. Giai đoạn: Pre-Seed. Trạng thái pipeline: Reviewing.",
            "Nhà sáng lập Cao Thị Ngọc từng là kỹ sư phần mềm và có gia đình kinh doanh 80 phòng trọ. Đội ngũ 6 người.",
            "Chủ nhà quản lý hợp đồng, chỉ số điện nước và gửi hóa đơn hằng tháng qua Zalo; người thuê thanh toán bằng mã QR.",
            "Thu phí 10.000 đồng mỗi phòng mỗi tháng.",
            "Có 1.900 chủ nhà sử dụng, quản lý 34.000 phòng. Tỷ lệ thanh toán đúng hạn của người thuê tăng từ 70% lên 88%.",
            "Đang gọi vốn 300.000 USD.",
            "Rủi ro: chủ nhà nhỏ lẻ nhạy cảm về giá, và khó mở rộng ra ngoài phân khúc nhà trọ công nhân.",
        ],
    },
    {
        "id": "buildmate",
        "name": "BuildMate",
        "lang": "en",
        "sections": [
            "BuildMate is a procurement marketplace for construction materials used by small contractors. Founded in 2022 in Da Nang. Stage: Seed. Pipeline status: New.",
            "CEO Luong Duc Minh ran a building-materials store for 9 years; CTO Kieu Anh Thu was a product engineer at an e-commerce company. 19 employees.",
            "Contractors request quotes for cement, steel and tiles; BuildMate aggregates orders from many sites to negotiate volume prices and offers 30-day payment terms.",
            "BuildMate earns a 6% margin on materials and a financing fee on deferred payments.",
            "Monthly GMV is 14 billion VND from 1,100 contractors. Repeat purchase rate is 68%.",
            "BuildMate is raising 2.2 million USD.",
            "Risks: working-capital needs from offering payment terms, and the cyclical construction market.",
        ],
    },
    # ---------------- HR / insurance ----------------
    {
        "id": "luongsom",
        "name": "LươngSớm",
        "lang": "vi",
        "sections": [
            "LươngSớm là dịch vụ ứng lương trước (earned wage access) cho công nhân nhà máy. Thành lập năm 2022 tại TP. Hồ Chí Minh. Giai đoạn: Series A. Trạng thái pipeline: Due Diligence.",
            "CEO Tạ Minh Châu từng làm giám đốc nhân sự tại một tập đoàn sản xuất giày. CTO Kha Văn Toàn từng là kỹ sư tại một công ty fintech. Đội ngũ 40 người.",
            "Công nhân rút trước tối đa 50% số lương đã làm qua ứng dụng; tiền được chuyển vào tài khoản trong 5 phút và tự động trừ vào kỳ lương.",
            "Doanh nghiệp không trả phí; người lao động trả phí cố định 15.000 đồng mỗi lần rút. Không tính lãi.",
            "LươngSớm hợp tác với 85 nhà máy, phục vụ 210.000 công nhân; mỗi tháng có 160.000 lượt rút với giá trị trung bình 1,1 triệu đồng.",
            "Đang gọi 7 triệu USD vòng Series A.",
            "Rủi ro: phụ thuộc vào việc tích hợp với hệ thống bảng lương của nhà máy, và nguy cơ bị xếp vào hoạt động cho vay tiêu dùng.",
        ],
    },
    {
        "id": "insurely",
        "name": "Insurely",
        "lang": "en",
        "sections": [
            "Insurely sells micro-insurance for motorbike ride-hailing drivers, embedded in driver apps. Founded in 2023 in Ho Chi Minh City. Stage: Seed. Pipeline status: Reviewing.",
            "CEO Chau Gia Huy was an actuary at a multinational insurer for 6 years. The team has 13 people.",
            "Drivers buy daily accident cover for 2,000 VND per day with one tap; claims are filed with photos and paid within 48 hours.",
            "Insurely is a licensed insurance agent and earns a 25% commission on premiums from its partner insurer.",
            "Insurely has 120,000 active policyholders and a claims ratio of 38%. Average claim payout time is 31 hours.",
            "Insurely is raising 1.8 million USD at an 8 million USD pre-money valuation.",
            "Risks: dependence on two ride-hailing partners for distribution, and fraud in small claims.",
        ],
    },
]


def render(memo: dict) -> str:
    lang = memo["lang"]
    note = (
        "> Synthetic deal memo (fictional company) created for a RAG demo."
        if lang == "en"
        else "> Bản ghi nhớ đầu tư giả lập (công ty hư cấu) dùng cho demo RAG."
    )
    parts = [f"# {memo['name']}", "", note, ""]
    for heading, body in zip(HEADINGS[lang], memo["sections"], strict=True):
        parts += [f"## {heading}", "", body, ""]
    return "\n".join(parts)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for memo in MEMOS:
        (OUT / f"{memo['id']}.md").write_text(render(memo), encoding="utf-8")
    print(f"wrote {len(MEMOS)} memos to {OUT}")


if __name__ == "__main__":
    main()
