// https://forum.arduino.cc/index.php?topic=632389.0

#define SDA_PORT PORTD
#define SDA_PIN 3
#define SCL_PORT PORTD
#define SCL_PIN 4

#define I2C_TIMEOUT 100
//#define I2C_FASTMODE 1


//We really want NDOF = 0x0C

#include <SoftWire.h>
#include <avr/io.h>
#include <Wire.h>

#define NODE_ADDRESS 18  // Change this unique address for each I2C slave node
#define PAYLOAD_SIZE 57 // Number of bytes  expected to be received by the master I2C node

SoftWire IMU_Wire = SoftWire();

int reading = 0;

float humidity = 0;
float temp = 0;
uint8_t readbuffer[6];

byte nodePayload[PAYLOAD_SIZE];

String toSend;

double prevAccel = 0;

void setup() {
  IMU_Wire.begin();
  Serial.begin(9600);
  //setup BNo055(IMU), ext clock, reset int, reset system, self test
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x3F));
  IMU_Wire.write(byte (0xE1));
  IMU_Wire.endTransmission();
  delay(1000);

  //read chip id register to see if IMU is working
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x00));
  IMU_Wire.endTransmission();
  IMU_Wire.requestFrom(0x28, 1);
  if (1 <= IMU_Wire.available()) {
    reading = IMU_Wire.read();
  }
  delay(250);

  //should be 160 (0xA0) if IMU is responding
  Serial.println(reading);
  //set IMU to IMU fusion mode
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x3D));
  IMU_Wire.write(byte (0x0C));
  IMU_Wire.endTransmission();

  //read mode register to see if IMU is in fusion mode (8)
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x3D));
  IMU_Wire.endTransmission();
  IMU_Wire.requestFrom(0x28, 1);
  if (1 <= IMU_Wire.available()) {
    reading = IMU_Wire.read();
  }
  pinMode(6, OUTPUT);
  delay(250);
  Serial.println(reading);
  Wire.begin(NODE_ADDRESS);  // Activate I2C network
  Wire.onRequest(requestEvent); // Request attention of master node
}

void loop() {
  toSend = "";

  //read calibration values
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x35));
  IMU_Wire.endTransmission();
  IMU_Wire.requestFrom(0x28, 1);
  uint8_t gyro = 0;
  uint8_t mag = 0;
  if (1 <= IMU_Wire.available()) {
    uint8_t readLSB = IMU_Wire.read();
    gyro = (readLSB >> 4) & 0x03;
    mag = readLSB & 0x03;
    /*Serial.print(gyro);
      Serial.print("  ");
      Serial.print(mag);
      Serial.print("  ");
    */

  }

  if ( gyro + mag == 6) {
    digitalWrite(6, LOW);
  } else if (gyro == 3 && mag < 3) {
    if ((millis() % 200) < 100) {
      digitalWrite(6, HIGH);
    } else {
      digitalWrite(6, LOW);
    }
  } else {
    digitalWrite(6, HIGH);
  }
  int pairs[8];
  int quats[4];
  //read all four Quaternion registers
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x20));
  IMU_Wire.endTransmission();
  IMU_Wire.requestFrom(0x28, 8);
  if (8 <= IMU_Wire.available()) {
    
    for(int i =0; i <8; i++){
      pairs[i] = IMU_Wire.read();
    }
    //each axis is 2 bytes,
    //shift MSB and combine bytes to get axis number
    double scale = (1.0 / (1 << 14));
    for (int i=0; i<4; i++){
       quats[i] =  pairs[ 0 + 2*i]|(pairs[1+2*i] << 8);
       
    }/*
    Serial.print(quats[1] * scale);
    Serial.print("  ");
    Serial.print(quats[2] * scale);
    Serial.print("  ");
    Serial.print(quats[3] * scale);
    Serial.print("  ");
    Serial.print(quats[0] * scale);
    Serial.print("  ");
    Serial.println();*/
  }
  double scale = (1.0 / (1 << 14));
  for (int i = 0; i < 4; i++) {
    //quats[i] = quats[i] * scale;
    toSend.concat(String(quats[i] * scale) + " ");
  }
  uint8_t buffers[6];
  int16_t x, y, z;
  x = y = z = 0;
  double xyz[3];
  IMU_Wire.beginTransmission(0x28);
  IMU_Wire.write(byte (0x28));
  IMU_Wire.endTransmission();
  IMU_Wire.requestFrom(0x28, 6);
  if (6 <= IMU_Wire.available()) {
    for (int i = 0; i < 6; i++) {
      buffers[i] = IMU_Wire.read();
    }
    x = ((int16_t)buffers[0]) | (((int16_t)buffers[1]) << 8);
    y = ((int16_t)buffers[2]) | (((int16_t)buffers[3]) << 8);
    z = ((int16_t)buffers[4]) | (((int16_t)buffers[5]) << 8);
  }
  xyz[0] = ((double)x) / 100.0;
  xyz[1] = ((double)y) / 100.0;
  xyz[2] = ((double)z) / 100.0;
  /*for(int i = 0; i < 3; i++){
    Serial.print(xyz[i]); Serial.print(" ");
    }*/
  double normaccel = sqrt(pow(xyz[0], 2) + pow(xyz[1], 2) + pow(xyz[2], 2) );
  double jerk = abs(normaccel - prevAccel + 0.001);
  prevAccel = normaccel;
  toSend.concat(String(jerk) + " ");



  // put your main code here, to run repeatedly:
  IMU_Wire.beginTransmission(0x44);
  byte meas_hirep[2] = {byte (0x24), byte (0x00)};
  IMU_Wire.write(meas_hirep, 2);
  IMU_Wire.endTransmission();
  IMU_Wire.requestFrom(0x44, 6);
  if (6 <= IMU_Wire.available()) {

    for (int i = 0; i < 6; i++) {
      readbuffer[i] = IMU_Wire.read();
    }
  }

  int32_t stemp = (int32_t)(((uint32_t)readbuffer[0] << 8) | readbuffer[1]);
  // simplified (65536 instead of 65535) integer version of:
  // temp = (stemp * 175.0f) / 65535.0f - 45.0f;
  stemp = ((4375 * stemp) >> 14) - 4500;
  temp = (float)stemp / 100.0f;
  uint32_t shum = ((uint32_t)readbuffer[3] << 8) | readbuffer[4];
  // simplified (65536 instead of 65535) integer version of:
  // humidity = (shum * 100.0f) / 65535.0f;
  shum = (625 * shum) >> 12;
  humidity = (float)shum / 100.0f;

  toSend.concat(String(temp) + " " + String(humidity) + " ");
  /*
    Serial.print(temp);
    Serial.print(" ");
    Serial.print(humidity);
    Serial.print(" ");
  */

  for (int i = A0; i < A4; i++) {
    int thermtemp = analogRead(i);
    toSend.concat(String(thermtemp) + " ");
    /*Serial.print(thermtemp);
      Serial.print(" ");*/
  }
  toSend.trim();
  Serial.println(toSend);
  toSend.getBytes(nodePayload, PAYLOAD_SIZE);
  
  delay(10);
}
void requestEvent()
{
  //Serial.print("wire request ");  // for debugging purposes. 
  //Serial.println(sizeof(toSend.c_str()));
  Wire.write(nodePayload, PAYLOAD_SIZE);  
  
  
  //Serial.println(String((char*)nodePayload)); // for debugging purposes. */
}
