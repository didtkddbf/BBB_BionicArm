#include <Wire.h>
#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx_i = Adafruit_MLX90614(0x5A);     //  index
Adafruit_MLX90614 mlx_r = Adafruit_MLX90614(0x5B);     //  rest
Adafruit_MLX90614 mlx_t = Adafruit_MLX90614(0x5C);     //  thumb

//Variables
int fan = 2;
int thumb = 3;
int index = 4;
int rest = 5;
float temp_t = 0;
float temp_i = 0;
float temp_r = 0;
int desired_t = 0;
int desired_i = 0;
int desired_r = 0;
int buff = 0;

void setup() {
  // initialize the serial communication:
  Serial.begin(9600);

  //Pins initialize
  pinMode(fan, OUTPUT);
  pinMode(thumb, OUTPUT);
  pinMode(index, OUTPUT);
  pinMode(rest, OUTPUT);
  digitalWrite(fan,LOW);
  analogWrite(thumb,0);
  analogWrite(index,0);
  analogWrite(rest,0);  

  ///////////      mlx.readObjectTempC()    //////////
  mlx_i.begin();       
  mlx_r.begin();       
  mlx_t.begin();
}

void loop() {
  if(Serial.available()){
    char state = Serial.read();
    Serial.println("state =");
    Serial.println(state);
    //Thumb
    
    if(state=='t'){
      while(1){
        if(Serial.available()){
        buff = Serial.parseInt();
        if(buff < 60){
          desired_t = buff;}
          break;}
    }}
  
   else if(state == 'i'){
      while(1){
        if(Serial.available()){
        buff = Serial.parseInt();
        if(buff < 60){
          desired_i = buff;}
          break;}
    }}
   
   else if(state == 'r'){
      while(1){
        if(Serial.available()){
        buff = Serial.parseInt();
        if(buff < 60){
          desired_r = buff;}
          break;}
    }}
   
   else if(state == 'c'){
   digitalWrite(fan,HIGH);
   Serial.println("Fan act");
   }
   
   else if(state == 's'){
    desired_t=0;
    desired_i=0;
    desired_r=0;  
    digitalWrite(fan,LOW);  
   }

   else{
    Serial.println("state =");
    Serial.println(state);
    Serial.println("No matching");
   }
   delay(100);
   }

///////////////////////Actuation//////////////////

  if(desired_t>0){
  temp_t = actuation('t', desired_t);}
  else{
    analogWrite(thumb,0);
    temp_t = mlx_t.readObjectTempC(); }
    
  if(desired_i>0){
  temp_i = actuation('i', desired_i);}
  else{
    analogWrite(thumb,0);
    temp_i = mlx_i.readObjectTempC(); }
    
  if(desired_r>0){
    temp_r = actuation('r', desired_r);}
  else{
    analogWrite(thumb,0);
    temp_r = mlx_r.readObjectTempC(); }
////////////////////////////////////////////////////


  //Temperature print
//  Serial.print(desired_t);
//  Serial.print("  ");
//  Serial.print(desired_i);
//  Serial.print("  ");
//  Serial.println(desired_r);
//  Serial.print(temp_t);
//  Serial.print("  ");
//  Serial.print(temp_i);
//  Serial.print("  ");
//  Serial.println(temp_r);
  delay(100);
}

float actuation(char finger, int desired_temp){
  float temp = 0;
  int error;
  int PWM;
  
  switch (finger) {
  case 't':
    temp = mlx_t.readObjectTempC();
    error = desired_temp - temp;
    if(error>0){
      PWM = 15 * error;
      analogWrite(thumb, PWM);
      Serial.println("Thumb Actuation");
    }
    else{
      analogWrite(thumb, 0);
    }
    break;
    
  case 'i':
    temp = mlx_i.readObjectTempC();
    error = desired_temp - temp;
    if(error>0){
      PWM = 15 * error;
      analogWrite(index, PWM);
    }
    else{
      analogWrite(index, 0);
    }
    break;
    
  case 'r':
    temp = mlx_r.readObjectTempC();
    error = desired_temp - temp;
    if(error>0){
      PWM = 15 * error;
      analogWrite(rest, PWM);
    }
    else{
      analogWrite(rest, 0);
    }
    break;
    
  default:
    break;
}
  return temp;
}
