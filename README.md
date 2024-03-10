﻿# TurretControlMiniPC

# Протокол обмена

## Передаваемые данные рабочего режима

|Байт|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|
|----|-|-|-|-|-|-|-|-|-|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'W' (0x57)|PositionMotor1 (byte 1)|PositionMotor1 (byte 2)|PositionMotor1 (byte 3)|PositionMotor1 (byte 4)|PositionMotor2 (byte 1)|PositionMotor2 (byte 2)|PositionMotor2 (byte 3)|PositionMotor2 (byte 4)|NeedPositionMotor1 (byte 1)|NeedPositionMotor1 (byte 2)|NeedPositionMotor1 (byte 3)|NeedPositionMotor1 (byte 4)|NeedPositionMotor2 (byte 1)|NeedPositionMotor2 (byte 2)|NeedPositionMotor2 (byte 3)|NeedPositionMotor2 (byte 4)|HPTurret/HitSensor|0|VideoStatus|0|0|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Ответ рабочего режима|Положение 1 двигателя|...|...|...|Положение 2 двигателя|...|...|...|Требуемое положение 1 двигателя|...|...|...|Требуемое положение 2 двигателя|...|...|...|Повреждение турели|Резерв|Статус видео передачи|Резерв|Резерв|Резерв|Резерв|Резерв|Резерв|Константа|Константа|

## Принимаемые данные рабочего режима

|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'C' (0x43)|motor1 (low)|motor1 (high)|motor2 (low)|motor2 (high)|trigger|0|0|0xA5|0xA5|
|Описание|Turret|Control|Команда управления турелью|кол-во шагов перемещения 1 двигателя low byte|кол-во шагов перемещения 1 двигателя high byte|кол-во шагов перемещения 2 двигателя low byte|кол-во шагов перемещения 2 двигателя high byte|Команда на срабатывание курка|Резерв|Резерв|Константа|Константа|

### Принимаемые значения
|Параметр|Значения|
|-|-|
|motor1|от -29999 до 29999, -30000, 30000 - непрерывное перемещение, motor1<0 - налево, motor1>0 - направо|
|motor2|от -29999 до 29999, -30000, 30000 - непрерывное перемещение, motor2<0 - вниз, motor2>0 - вверх|
|trigger|0 - выкл / 1 - вкл|
|hit_sensor|0 - 0xFF|

## Команды работы с датчиком вибрации

### Установка задержки срабатывания
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'S' (0x53)|P (0x50)|D (0x44)|0-Установить/1-прочитать|Delay (low)|Delay (high)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Sensor|Parameters|Delay|Read|Задержка повторного срабатывания сенсора, мс|...|Резерв|Резерв|Константа|Константа|

### Установка количества HP
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'S' (0x53)|P (0x50)|H (0x48)|0-Установить/1-прочитать|Health (low)|Health (high)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Sensor|Parameters|HP|Read|Количество HP, шт|...|Резерв|Резерв|Константа|Константа|

### Установка минут до сгорания HP
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'S' (0x53)|P (0x50)|M (0x4D)|0-Установить/1-прочитать|Minutes (low)|Minutes (high)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Sensor|Parameters|Minutes Delay|Read|Задерка до сгорания урона, мин|...|Резерв|Резерв|Константа|Константа|

### Установка секунд до сгорания HP
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'S' (0x53)|P (0x50)|S (0x53)|0-Установить/1-прочитать|Seconds (low)|Seconds (high)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Sensor|Parameters|Seconds Delay|Read|Задерка до сгорания урона, сек|...|Резерв|Резерв|Константа|Константа|

### Сброс урона
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'S' (0x53)|'F' (0x46)|R (0x52)|0|ResetDamage|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Sensor|Flag|Reset damage|Read|Сброс урона|Резерв|Резерв|Резерв|Константа|Константа|

|Параметр|Значения|
|-|-|
|Delay|0...32,767|
|Health|0...120|
|Minutes|0...32,767|
|Seconds|0...32,767|
|ResetDamage|0/1|

## Команды работы с видео

### Включение/Выключение передачи видео
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'V' (0x56)|'S' (0x53)|1-вкл/0-выкл|0|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Video|Start/Stop|команда|Резерв|Резерв|Резерв|Резерв|Резерв|Константа|Константа|

### Задание высоты изображения Height
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'V' (0x56)|'H' (0x48)|Height (low)|Height (high)|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Video|Height|Высота передаваемого изображения|Высота передаваемого изображения|Резерв|Резерв|Резерв|Резерв|Константа|Константа|

### Задание ширины изображения Width
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'V' (0x56)|'W' (0x57)|Width (low)|Width (high)|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Video|Width|Ширина передаваемого изображения|Ширина передаваемого изображения|Резерв|Резерв|Резерв|Резерв|Константа|Константа|

### Задание битрейта
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'V' (0x56)|'B' (0x42)|Bitrate (byte 1)|Bitrate (byte 2)|Bitrate (byte 3)|Bitrate (byte 4)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Video|Bitrate|Битрейт|Битрейт|Битрейт|Битрейт|Резерв|Резерв|Константа|Константа|

### Задание кадров в секунду
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'V' (0x56)|'F' (0x46)|Framerate (low)|Framerate (high)|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Video|Framerate|Кадров в секунду|Кадров в секунду|Резерв|Резерв|Резерв|Резерв|Константа|Константа|

### Задание порта на прием видео данных
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'V' (0x56)|'P' (0x50)|Port (low)|Port (high)|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Video|Port|Номер порта|Номер порта|Резерв|Резерв|Резерв|Резерв|Константа|Константа|

### Принимаемые значения
|Параметр|Значения|
|-|-|
|Height|0-0xFFFF|
|Width|0-0xFFFF|
|Bitrate|0-0xFFFFFFFF|
|Framerate|0-0xFFFF|
|Port|0-0xFFFF|

## Установка параметров движения

### Максимальное и минимальное количество шагов из нулевого положения 
|Байт|1|2|3|4| 5                        |6| 7                                                    |8|9|10|11|12|
|----|-|-|-|-|--------------------------|-|------------------------------------------------------|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'P' (0x50)| 0x01                     |0-Установить/1-прочитать| MaxSteppersStepMotor1 (Byte 1)                       |MaxSteppersStepMotor1 (Byte 2)|MaxSteppersStepMotor1 (Byte 3)|MaxSteppersStepMotor1 (Byte 4)|0xA5|0xA5|
|Описание|Turret|Control|Movement|Parameters| MaxPositionStepMotor1 |Reade| Максимальное положение 1 двигателя (микрошагов от 0) |...|...|...|Константа|Константа|

|Байт|1|2|3|4| 5                     |6| 7                                                    |8|9|10|11|12|
|----|-|-|-|-|-----------------------|-|------------------------------------------------------|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'P' (0x50)| 0x02                  |0-Установить/1-прочитать| MaxSteppersStepMotor2 (Byte 1)                       |MaxSteppersStepMotor2 (Byte 2)|MaxSteppersStepMotor2 (Byte 3)|MaxSteppersStepMotor2 (Byte 4)|0xA5|0xA5|
|Описание|Turret|Control|Movement|Parameters| MaxPositionStepMotor2 |Reade| Максимальное положение 2 двигателя (микрошагов от 0) |...|...|...|Константа|Константа|

|Байт|1|2|3|4| 5                     |6| 7                                                   |8|9|10|11|12|
|----|-|-|-|-|-----------------------|-|-----------------------------------------------------|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'P' (0x50)| 0x03                  |0-Установить/1-прочитать| MaxSteppersStepMotor1 (Byte 1)                      |MaxSteppersStepMotor1 (Byte 2)|MaxSteppersStepMotor1 (Byte 3)|MaxSteppersStepMotor1 (Byte 4)|0xA5|0xA5|
|Описание|Turret|Control|Movement|Parameters| MinPositionStepMotor1 |Reade| Минимальное положение 1 двигателя (микрошагов от 0) |...|...|...|Константа|Константа|

|Байт|1|2|3|4| 5                     |6| 7                                                   |8|9|10|11|12|
|----|-|-|-|-|-----------------------|-|-----------------------------------------------------|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'P' (0x50)| 0x04                  |0-Установить/1-прочитать| MaxSteppersStepMotor2 (Byte 1)                      |MaxSteppersStepMotor2 (Byte 2)|MaxSteppersStepMotor2 (Byte 3)|MaxSteppersStepMotor2 (Byte 4)|0xA5|0xA5|
|Описание|Turret|Control|Movement|Parameters| MinPositionStepMotor2 |Reade| Минимальное положение 2 двигателя (микрошагов от 0) |...|...|...|Константа|Константа|

### Включение движения без ограничений
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'F' (0x46)|'L' (0x4C)|0|FlagNoLimitStepMotor|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Movement|Flag|NoLimitStepMotor|Reade|Флаг включения движения без ограничений|Резерв|Резерв|Резерв|Константа|Константа|

### Задать нулевое положение
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'F' (0x46)|'Z' (0x5A)|0|FlagZeroPosition|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Movement|Flag|ZeroPosition|Reade|Установить нулевое положение|Резерв|Резерв|Резерв|Константа|Константа|

### Частота генерации сигнала на вращение
|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'P' (0x50)|0x11|0-Установить/1-прочитать|FreqMotor1 (low)|FreqMotor1 (high)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Movement|Parameters|FreqMotor 1|Reade|Частота управления шаговым двигателем 1, Гц|...|Резерв|Резерв|Константа|Константа|

|Байт|1|2|3|4|5|6|7|8|9|10|11|12|
|----|-|-|-|-|-|-|-|-|-|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|'M' (0x56)|'P' (0x50)|0x12|0-Установить/1-прочитать|FreqMotor2 (low)|FreqMotor2 (high)|0|0|0xA5|0xA5|
|Описание|Turret|Control|Movement|Parameters|FreqMotor 2|Reade|Частота управления шаговым двигателем 2, Гц|...|Резерв|Резерв|Константа|Константа|

### Принимаемые значения
| Параметр              |Значения|
|-----------------------|-|
| MaxPositionStepMotor1 |от −2 147 483 648 до 2 147 483 647|
| MaxPositionStepMotor2 |от −2 147 483 648 до 2 147 483 647|
| MinPositionStepMotor1 |от −2 147 483 648 до 2 147 483 647|
| MinPositionStepMotor2 |от −2 147 483 648 до 2 147 483 647|
| FlagNoLimitStepMotor  |1-выкл ограничения/0-Нормальный режим работы|
| FlagZeroPosition      |1-Турель в нулевой позиции (Сброс счетчиков положения)/0-Нормальный режим работы|
| FreqMotor1            |0-1000|
| FreqMotor2            |0-1000|

## Ответ на установку/чтетение параметров

|Байт|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|
|----|-|-|-|-|-|-|-|-|-|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|
|Значение|'T' (0x54)|'C' (0x43)|Module|'P' 0x50|NumberParameters|value (byte 1)|value (byte 2)|value (byte 3)|value (byte 4)|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0xA5|0xA5|
|Описание|Turret|Control|Имя модуля|Флаг параметра|Номер параметра|Значение|...|...|...|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|Константа|Константа|
