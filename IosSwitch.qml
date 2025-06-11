import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property bool checked: false
    signal toggled(bool checked)

    width: 52
    height: 32

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 16
        color: root.checked ? "#4cd964" : "#393939"
        border.color: "transparent"
        border.width: 0

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.checked = !root.checked
                root.toggled(root.checked)
            }
        }
    }

    Rectangle {
        id: knob
        width: 28
        height: 28
        radius: 14
        y: 2
        color: "white"
        x: root.checked ? 22 : 2
        Behavior on x { NumberAnimation { duration: 120; easing.type: Easing.InOutQuad } }
        z: 2
        border.color: "#dddddd"
        border.width: 0
    }
}