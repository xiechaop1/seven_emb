import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 400
    height: 200
    color: "#18181a"

    property int religionIndex: religionWheel.currentIndex
    property var religions: [
        "无宗教信仰", "佛教", "基督教", "伊斯兰教", "印度教", "道教", "其他"
    ]

    FlickableWheel {
        id: religionWheel
        width: 300
        height: 160
        model: religions.length
        delegate: Text {
            text: religions[index]
            font.pixelSize: 32
            color: religionWheel.currentIndex === index ? "white" : "#8e8e93"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}