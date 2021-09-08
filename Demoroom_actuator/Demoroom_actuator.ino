//pin for fan
int fan1 = 10; //Fan on left side bundle
int fan2 = 9; //Fan on right side fabric
//pin for actuator
int act1 = 5; //actuating left side(bundled actuator)
int act2 = 6; //LED all side(fabric actuator)
//pint for switch
int swc1 = 7; //switch of white
int swc2 = 8; //switch of yellow
int swc3 = 2; //switch of red
int led = 4; //switch button led
int act3 = 3; //actuating right side(fabric actuator) using 24V SMPS
//values
int i;
int cycle = 1; //cycle of actuation
int Tact = 2200; //actuating time on left
int Tact2 = 4000; //actuating time on right
int Tcool = 10000; //cooling time on left
int Tcool2 = 15000; //cooling time on right
int actTime;
int coolTime;
int timer = 100;
//int checker = 0;
String test;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  //pin I/O setting
  pinMode(fan1, OUTPUT);
  pinMode(fan2, OUTPUT);
  pinMode(act1, OUTPUT);
  pinMode(act2, OUTPUT);
  pinMode(act3, OUTPUT);
  pinMode(swc1, INPUT_PULLUP);
  pinMode(swc2, INPUT_PULLUP);
  pinMode(swc3, INPUT_PULLUP);
  pinMode(led, OUTPUT);
//  attachInterrupt(0, Stop, FALLING);

  //pin intial setting
  digitalWrite(fan1, HIGH);
  digitalWrite(fan2, HIGH);
  digitalWrite(act1, LOW);
  digitalWrite(act2, LOW);
  digitalWrite(act3, HIGH);
  digitalWrite(led, LOW);

  Serial.setTimeout(10);
}

void loop() {
  // put your main code here, to run repeatedly:

  if (digitalRead(swc1) == LOW) //White button clicked actuator on left side, bundled actuator, cycle on
  {
    digitalWrite(led, HIGH);
    for (i = 0; i<cycle; i++)
    {
      actTime = 0;
      coolTime = 0;
      while (digitalRead(swc3) == HIGH)
      {
        digitalWrite(act1, HIGH);
        digitalWrite(act2, HIGH);
        delay(timer);
        actTime = actTime + 1;
        if (actTime > Tact/timer)
        {
          digitalWrite(act1, LOW);
          break;
        }
      }
      while (digitalRead(swc3) == HIGH)
      {
        digitalWrite(fan1, LOW);
        delay(timer);
        coolTime = coolTime + 1;
        if (coolTime > Tcool/timer)
        {
          digitalWrite(fan1, HIGH);
          break;
        }
      }
      if (digitalRead(swc3) == LOW)
      {
        digitalWrite(act1, LOW);
        digitalWrite(act2, LOW);
        digitalWrite(fan1, LOW);
        delay(Tcool);
        digitalWrite(fan1, HIGH);
        Serial.println("Stop");
        break;
      }
    }
    digitalWrite(led, LOW);
  }

  else if (digitalRead(swc2) == LOW) //Yellow button clicked actuator on right side, fabric actuator, cycle on
  {
    digitalWrite(led, HIGH);
    for (i = 0; i<cycle; i++)
    {
      actTime = 0;
      coolTime = 0;
      while (digitalRead(swc3) == HIGH)
      {
        digitalWrite(act2, HIGH);
        digitalWrite(act3, LOW);
        delay(timer);
        actTime = actTime + 1;
        if (actTime > Tact2/timer)
        {
          digitalWrite(act2, LOW);
          digitalWrite(act3, HIGH);
          break;
        }
      }
      while (digitalRead(swc3) == HIGH)
      {
        digitalWrite(fan2, LOW);
        digitalWrite(act2, HIGH);
        delay(timer);
        coolTime = coolTime + 1;
        if (coolTime > Tcool2/timer)
        {
          digitalWrite(fan2, HIGH);
          digitalWrite(act3, HIGH);
          digitalWrite(act2, LOW);
          break;
        }
      }          
      if (digitalRead(swc3) == LOW)
      {
        digitalWrite(act2, LOW);
        digitalWrite(act3, HIGH);
        digitalWrite(fan2, LOW);
        delay(Tcool);
        digitalWrite(fan2, HIGH);
        Serial.println("Stop");
        break;
      }
          digitalWrite(fan2, HIGH);
          digitalWrite(act3, HIGH);
          digitalWrite(act2, LOW);
    }
    digitalWrite(led, LOW);
  }

  else if (digitalRead(swc3) == LOW)
  {
    digitalWrite(led, HIGH);
    digitalWrite(fan1, LOW);
    digitalWrite(fan2, LOW);
    delay(2000);
    digitalWrite(fan1, HIGH);
    digitalWrite(fan2, HIGH);
    digitalWrite(led, LOW);
  }
////////////////////////////////////////
  //Test code
  if (Serial.available())
  {
    test = Serial.readString();

    if (test == "1")
    {
      digitalWrite(fan1, LOW);
      Serial.println("Fan1 on");
    }

    else if (test == "11")
    {
      digitalWrite(fan1, HIGH);
      Serial.println("Fan1 off");
    }

    else if (test == "2")
    {
      digitalWrite(fan2, LOW);
      Serial.println("Fan2 on");
    }

    else if (test == "22")
    {
      digitalWrite(fan2, HIGH);
      Serial.println("Fan2 off");
    }

    else if (test == "3")
    {
      digitalWrite(act1, HIGH);
      Serial.println("Actuator1 & LED1 on");
    }

    else if (test == "33")
    {
      digitalWrite(act1, LOW);
      Serial.println("Actuator1 & LED1 off");
    }

    else if (test == "4")
    {
      digitalWrite(act2, HIGH);
      Serial.println("Actuator2 & LED2 on");
    }

    else if (test == "44")
    {
      digitalWrite(act2, LOW);
      Serial.println("Actuator2 & LED2 off");
    }

    else if (test == "5")
    {
      digitalWrite(act3, LOW);
      Serial.println("24V on");      
    }

    else if (test == "55")
    {
      digitalWrite(act3, HIGH);
      Serial.println("24V off");
    }

    else if (test == "6")
    {
      digitalWrite(led, LOW);
      Serial.println("LED on");
    }

    else if (test == "66")
    {
      digitalWrite(led, HIGH);
      Serial.println("LED off");
    }

    else if (test == "0")
    {
      digitalWrite(fan1, HIGH);
      digitalWrite(fan2, HIGH);
      digitalWrite(act1, LOW);
      digitalWrite(act2, LOW);
      digitalWrite(led, HIGH);
      Serial.println("All device off");
    }

    else if (test == "swc")
    {
      while (Serial.readString() != "end")
      {
        Serial.print(digitalRead(swc1));
        Serial.print(" ");
        Serial.print(digitalRead(swc2));
        Serial.print(" ");
        Serial.println(digitalRead(swc3));        
      }
    }
  }
////////////////////////////////////////
}

//void Stop(){
//  Serial.println("Go");
////  checker = 1;
////  digitalWrite(act1, LOW);
////  digitalWrite(act2, LOW);
////  digitalWrite(fan1, HIGH);
////  digitalWrite(fan2, HIGH);
////  delay(Tcool/5);
////  digitalWrite(fan1, LOW);
////  digitalWrite(fan2, LOW);
//  delayMicroseconds(10000);
//  if(digitalRead(swc3) != LOW)
//  {
//    return;
//  }
//}
