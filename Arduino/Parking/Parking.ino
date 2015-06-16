#include <Servo.h>


const int  button_in = 2; 
const int  button_out = 4; 
const int led_green = 8;
const int in_servo_pin = 5;
const int out_servo_pin = 6;
const int led_out = 10;
const int led_red = 9;
const int nb_slots = 9;
const int gate_op_time = 5000; // ms

int state_b_in = 0; // current state of the button in
int state_b_out = 0; 
int pstate_b_in = 0; // previous state of the button in
int pstate_b_out = 0;


String data_out = String("<");
String rcvd_data = ""; 
String data_in = "";

boolean new_data = false;

int g1_opened = 0;
int g2_opened = 0;
int i = 5;
unsigned long time_g1 = 0;
unsigned long time_g2 = 0;
unsigned long time = 0;
boolean gate_state_changed = false;

Servo inServo;
Servo outServo;


void setup()
{
  pinMode(button_in, INPUT); 
  pinMode(button_out, INPUT); 
  pinMode(led_red, OUTPUT);
  pinMode(led_green, OUTPUT);
  pinMode(led_out, OUTPUT);
  Serial.begin(9600);
  inServo.attach(in_servo_pin);
  inServo.write(90);
  outServo.attach(out_servo_pin);
  outServo.write(90);

}

void sendState()
{
  data_out = "<00";
  
  
  state_b_in = digitalRead(button_in);
  state_b_out = digitalRead(button_out);

  if ((state_b_in != pstate_b_in) || (state_b_out != pstate_b_out) || gate_state_changed)
  {
    
    if (state_b_in != pstate_b_in)
    {
      pstate_b_in = state_b_in; 
      
      if (state_b_in != 0)
      {
        data_out[1]='1';
      }
       
      else 
      {
        data_out[1]='0';  
      }
      
    }
  
  
    if (state_b_out != pstate_b_out)
    {
      pstate_b_out = state_b_out; 
      
      if (state_b_out != 0)
      {
        data_out[2]='1'; 
      }
        
      else 
      {
        data_out[2]='0';   
      }
    }
      //Serial.println(data_out);
    
    data_out = data_out + String(g1_opened);
    data_out = data_out + String(g2_opened);
    data_out = data_out + ">";
    gate_state_changed = false;
    Serial.println(data_out);
  }
  else
  {
    data_out = "<0000>";
    gate_state_changed = false;
  }
}

void GetData()
{
  static boolean rcv_in_prog = false;
  static byte ndx = 0;
  char startMark = '<';
  char endMark = '>';
  char rc;

  if (Serial.available() > 0)
  {
    while (Serial.available() > 0 && new_data == false) {
      rc = Serial.read();
    
      if (rcv_in_prog == true)
      {
      
        if (rc != endMark)
        {
          rcvd_data += String(rc);
        }
        
        else
        {
          rcv_in_prog = false;
          new_data = true;
        }
      }
    
      else if (rc == startMark)
      {
        rcv_in_prog = true;
        rcvd_data = "";
      
      } 
    }
  
  
  } 
  data_in = rcvd_data; 
}    

void Execute()
{
  time = millis();
  if (new_data == true)

  {

    if ((data_in[0] == '1') && (g1_opened == 0))
    {
      time_g1 = time;
      g1_opened = 1;
      inServo.write(0);     
      digitalWrite(led_green, HIGH);
      gate_state_changed = true;
      digitalWrite(led_red, LOW); 
      

      
    }
    
    else if (data_in[0] == '1')
    {
     time_g1 = time;
    } 
      
      
    if ((data_in[1] == '1') && (g2_opened == 0))
    {
      time_g2 = time;
      g2_opened = 1;
      outServo.write(0);
      digitalWrite(led_out, HIGH); 
      gate_state_changed = true;
      digitalWrite(led_red, LOW); 
    }
    
    else if (data_in[1] == '1')
    {
     time_g2 = time;
    } 
    
    
    if (data_in[2]=='1')
    {
      digitalWrite(led_red, HIGH); 
    }
    new_data = false;
  }

  if ((time-time_g1 >= gate_op_time) && (g1_opened == 1))
  {
    time_g1 = 0;
    g1_opened = 0;
    inServo.write(90);
    digitalWrite(led_green, LOW);
    data_in[0] = 'X';
    gate_state_changed = true;    
  }
  
  if ((time-time_g2 >= gate_op_time) && (g2_opened == 1))
  {
    time_g2 = 0;
    g2_opened = 0;
    outServo.write(90);
    digitalWrite(led_out, LOW);
    data_in[1] = 'X';
    gate_state_changed = true;
  }


    
}


void loop()
{
  
  GetData();
  Execute();
  SendState();

}












