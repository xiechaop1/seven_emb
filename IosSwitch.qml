import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property bool checked: false
    signal toggled(bool checked)

    width: 52
    height: 32

    // 背景轨道
    Rectangle {
        id: track
        anchors.fill: parent
        radius: height / 2
        color: root.checked ? "#34C759" : "#D1D1D6"  // iOS风格绿色和灰色
        border.color: "transparent"
        z: 0
    }

    // 拖动圆钮（白色圆形）
    Rectangle {
        id: knob
        width: 28
        height: 28
        radius: 14
        y: 2
        x: root.checked ? 22 : 2
        color: "white"
        border.color: "#CCCCCC"
        border.width: 1
        z: 2

        Behavior on x {
            NumberAnimation { duration: 160; easing.type: Easing.InOutQuad }
        }
        
    }

    // 点击区域
    MouseArea {
        anchors.fill: parent
        onClicked: {
            root.checked = !root.checked
            root.toggled(root.checked)
        }
    }
}