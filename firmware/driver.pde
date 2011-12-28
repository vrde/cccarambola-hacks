/*
  Nathan Seidle
  SparkFun Electronics 2011
  
  Mod by Marco Brianza to get data from serial port
  
  This code is public domain but you buy me a beer if you use this and we meet someday (Beerware license).
  
  Controlling an LED strip with individually controllable RGB LEDs. This stuff is awesome.
  
  The SparkFun (individually controllable) RGB strip contains a bunch of WS2801 ICs. These
  are controlled over a simple data and clock setup. The WS2801 is really cool! Each IC has its
  own internal clock so that it can do all the PWM for that specific LED for you. Each IC
  requires 24 bits of 'greyscale' data. This means you can have 256 levels of red, 256 of blue,
  and 256 levels of green for each RGB LED. REALLY granular.
 
  To control the strip, you clock in data continually. Each IC automatically passes the data onto
  the next IC. Once you pause for more than 500us, each IC 'posts' or begins to output the color data
  you just clocked in. So, clock in (24bits * 32LEDs = ) 768 bits, then pause for 500us. Then
  repeat if you wish to display something new.
  
  This example code will display bright red, green, and blue, then 'trickle' random colors down 
  the LED strip.
  
  You will need to connect 5V/Gnd from the Arduino (USB power seems to be sufficient).
  
  For the data pins, please pay attention to the arrow printed on the strip. You will need to connect to
  the end that is the begining of the arrows (data connection)--->
  
  If you have a 4-pin connection:
  Blue = 5V
  Red = SDI
  Green = CKI
  Black = GND
  
  If you have a split 5-pin connection:
  2-pin Red+Black = 5V/GND
  Green = CKI
  Red = SDI
 */
 
 

int SDI = 2; //Red wire (not the red 5V wire!)
int CKI = 3; //Green wire
int ledPin = 13; //On board LED

#define STRIP_LENGTH  32 //32 LEDs on this strip
#define STRIP_LENGTH_B  32 * 3

long strip_colors[STRIP_LENGTH];

long BREAK_INTERVAL=1000; //interval to activate LED data

int i; //strip_colors position to fill the array

#include <stdarg.h>

void setup() {
  pinMode(SDI, OUTPUT);
  pinMode(CKI, OUTPUT);
  pinMode(ledPin, OUTPUT);
  
  
  //Clear out the array
  for(int x = 0 ; x < STRIP_LENGTH ; x++)
    strip_colors[x] = 0;
    
  
  //Pre-fill the color array with known values to test strip
  strip_colors[0] = 0x100000; // Red
  strip_colors[1] = 0x001000; // Green
  strip_colors[2] = 0x000010; // Blue
  strip_colors[3] = 0x101000; // Blue
  post_frame(); //Push the current color frame to the strip
  
  Serial.begin(115200);
}

void loop() {
    // read from serial port --------------------------
  int ok = 1;
  if (Serial.available() >= STRIP_LENGTH_B) {
    for(int i = 0; i < STRIP_LENGTH; i++) {
        char r = Serial.read();
        if (r == '\254') { ok = 0; break; }
        char g = Serial.read();
        if (g == '\254') { ok = 0; break; }
        char b = Serial.read();
        if (b == '\254') { ok = 0; break; }
        strip_colors[i] = (long)r << 16 | (long)g << 8 | (long)b;
        //strip_colors[i] = 0xff << 16;
      }
    if (ok) post_frame();
  }
}//--------------------------------------------------------------------end loop


//Takes the current strip color array and pushes it out
void post_frame (void) {
  //Each LED requires 24 bits of data
  //MSB: R7, R6, R5..., G7, G6..., B7, B6... B0 
  //Once the 24 bits have been delivered, the IC immediately relays these bits to its neighbor
  //Pulling the clock low for 500us or more causes the IC to post the data.

  for(int LED_number = 0 ; LED_number < STRIP_LENGTH ; LED_number++) {
    long this_led_color = strip_colors[LED_number]; //24 bits of color data

    for(byte color_bit = 23 ; color_bit != 255 ; color_bit--) {
      //Feed color bit 23 first (red data MSB)
      
      digitalWrite(CKI, LOW); //Only change data when clock is low
      
      long mask = 1L << color_bit;
      //The 1'L' forces the 1 to start as a 32 bit number, otherwise it defaults to 16-bit.
      
      if(this_led_color & mask) 
        digitalWrite(SDI, HIGH);
      else
        digitalWrite(SDI, LOW);
  
      digitalWrite(CKI, HIGH); //Data is latched when clock goes high
    }
  }

  //Pull clock low to put strip into reset/post mode
  digitalWrite(CKI, LOW);
  delayMicroseconds(500); //Wait for 500us to go into reset
}
