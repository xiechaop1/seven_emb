import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 400
    height: 200
    color: "#18181a"

    property int year: yearWheel.currentIndex + startYear
    property int month: monthWheel.currentIndex + 1
    property int day: dayWheel.currentIndex + 1

    property int startYear: 2010
    property int endYear: 2030

    Row {
        anchors.centerIn: parent
        spacing: 16

        FlickableWheel {
            id: yearWheel
            width: 100
            height: 160
            model: endYear - startYear + 1
            delegate: Text {
                text: (index + startYear).toString()
                font.pixelSize: 32
                color: yearWheel.currentIndex === index ? "white" : "#8e8e93"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
        FlickableWheel {
            id: monthWheel
            width: 80
            height: 160
            model: 12
            delegate: Text {
                text: (index + 1).toString().padStart(2, '0')
                font.pixelSize: 32
                color: monthWheel.currentIndex === index ? "white" : "#8e8e93"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
        FlickableWheel {
            id: dayWheel
            width: 80
            height: 160
            model: {
                var m = monthWheel.currentIndex + 1
                var y = yearWheel.currentIndex + startYear
                if (m === 2) {
                    if ((y % 4 === 0 && y % 100 !== 0) || (y % 400 === 0))
                        return 29
                    else
                        return 28
                }
                if ([1,3,5,7,8,10,12].indexOf(m) !== -1)
                    return 31
                return 30
            }
            delegate: Text {
                text: (index + 1).toString().padStart(2, '0')
                font.pixelSize: 32
                color: dayWheel.currentIndex === index ? "white" : "#8e8e93"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}