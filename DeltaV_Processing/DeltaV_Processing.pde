import processing.video.*;

Capture vstream;

void setup() {
  size(800, 600);
  
  vstream = new Capture(this, 800, 600, "/dev/video2");
  vstream.start();
  
  for (String device : Capture.list()) {
    println("Device available: " + device);
  }
}

void draw() {
  image(vstream, 0, 0);
}

void captureEvent(Capture video) {
  video.read();
}
