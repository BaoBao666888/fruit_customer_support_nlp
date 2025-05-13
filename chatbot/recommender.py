import random

def suggest_product():
    options = [
        "Bạn nên thử xoài cát Hòa Lộc – rất ngọt và đang vào mùa.",
        "Sầu riêng Ri6 đang được giảm giá trong tuần này.",
        "Táo Fuji giòn, ngọt, dễ bảo quản – rất đáng mua!",
        "Nho Mỹ đang vào mùa, rất tươi ngon và bổ dưỡng.",
        "Bưởi da xanh có vị ngọt thanh, rất thích hợp cho mùa hè.",
        "Dưa hấu không hạt rất ngọt, thích hợp cho những ngày nắng nóng.",
        "Chanh dây có thể dùng để làm nước giải khát rất ngon.",
        "Mít tố nữ có vị ngọt, thơm, rất được yêu thích.",
        "Cam sành có vị ngọt, chua nhẹ, rất tốt cho sức khỏe.",
        "Quýt đường có vị ngọt, dễ ăn, rất thích hợp cho trẻ em.",
        "Ổi lê có vị ngọt, giòn, rất tốt cho tiêu hóa.",
        "Dưa lưới có vị ngọt, mát, rất thích hợp cho mùa hè.",
        "Măng cụt có vị ngọt, thanh mát, rất tốt cho sức khỏe.",
        "Nhãn lồng Hưng Yên có vị ngọt, thơm, rất được yêu thích.",
        "Xoài cát có vị ngọt, thơm, rất thích hợp cho mùa hè.",
        "Bơ sáp có vị béo, ngậy, rất tốt cho sức khỏe.",
        "Dâu tây có vị ngọt, chua nhẹ, rất thích hợp cho mùa hè.",
        "Cherry có vị ngọt, chua nhẹ, rất tốt cho sức khỏe.",
        "Mận xôi có vị ngọt, thơm, rất thích hợp cho mùa hè.",
        "Lê Hàn Quốc có vị ngọt, giòn, rất tốt cho sức khỏe.",
    ]
    return random.choice(options)
