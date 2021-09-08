//pin for fan
int fan1 = 3; //Fan on left side bundle
//int fan2 = 9; //Fan on right side fabric
//pin for actuator
int act1 = 6; //actuating left side(bundled actuator)
int act2 = 5; //LED all side(fabric actuator)
//pint for switch
int swc1 = 7; //switch of white
int swc3 = 8; //switch of red
int led = 4; //switch button led
//values
int i;
int cycle = 1; //cycle of actuation
int Tact = 1900; //actuating time on left
int Tcool = 10000; //cooling time on left
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
  pinMode(act1, OUTPUT);
  pinMode(act2, OUTPUT);
  pinMode(swc1, INPUT_PULLUP);
  pinMode(swc3, INPUT_PULLUP);
  pinMode(led, OUTPUT);
//  attachInterrupt(0, Stop, FALLING);

  //pin intial setting
  digitalWrite(fan1, HIGH);
  digitalWrite(act1, HIGH);
  digitalWrite(act2, HIGH);
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
        digitalWrite(act1, LOW);
        digitalWrite(act2, LOW);
        delay(timer);
        actTime = actTime + 1;
        if (actTime > Tact/timer)
        {
          digitalWrite(act1, HIGH);
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
          digitalWrite(act2, HIGH);
          break;
        }
      }
      if (digitalRead(swc3) == LOW)
      {
        digitalWrite(act1, HIGH);
        digitalWrite(act2, HIGH);
        digitalWrite(fan1, LOW);
        delay(Tcool);
        digitalWrite(fan1, HIGH);
        Serial.println("Stop");
        break;
      }
    }
    digitalWrite(led, LOW);
  }

  else if (digitalRead(swc3) == LOW)
  {
    digitalWrite(led, HIGH);
    digitalWrite(fan1, LOW);
    delay(2000);
    digitalWrite(fan1, HIGH);
    digitalWrite(led, LOW);
  }
////////////////////////////////////////
  //Test code
  if (Serial.available())
  {
    test = Serial.readString();

    if (test == "1")
  {
    Serial.println(test);
    digitalWrite(led, HIGH);
    for (i = 0; i<cycle; i++)
    {
      actTime = 0;
      coolTime = 0;
      while (digitalRead(swc3) == HIGH)
      {
        digitalWrite(act1, LOW);
        digitalWrite(act2, LOW);
        delay(timer);
        actTime = actTime + 1;
        if (actTime > Tact/timer)
        {
          digitalWrite(act1, HIGH);
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
          digitalWrite(act2, HIGH);
          break;
        }
      }
      if (digitalRead(swc3) == LOW)
      {
        digitalWrite(act1, HIGH);
        digitalWrite(act2, HIGH);
        digitalWrite(fan1, LOW);
        delay(Tcool);
        digitalWrite(fan1, HIGH);
        Serial.println("Stop");
        break;
      }
    }
    digitalWrite(led, LOW);
  }

    else if (test == "0")
    {
      digitalWrite(fan1, HIGH);
//      digitalWrite(fan2, HIGH);
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
        Serial.println(digitalRead(swc3));        
      }
    }
  }
}
////////////////////////////////////////


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
