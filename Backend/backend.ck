// globals

"localhost" => string HOST;
3001        => int PORT_OUT;
3000        => int PORT_IN;
6           => int LOOPS_COUNT;
8::second   => dur LOOP_DURATION;
0.01        => float EPS;

// loops

class Loop {
  LiSa loop;
  Gain loopGain;
  int dir;

  int isPlaying;
  int isRecording;

  fun void init(Gain input) {
    LOOP_DURATION => loop.duration;

    1 => dir;

    1 => loop.loop;
    1 => loop.loopRec;
    1 => loop.maxVoices;

    // -1.0 => loop.rate; // works!

    input => loop => loopGain => dac;
  }

  fun int play(int status) {
    status => loop.play;
    status => isPlaying;

    return isPlaying;
  }

  fun int play() {
    return isPlaying;
  }

  fun int record(int status) {
    if (status) {
      loop.playPos() => loop.recPos;
      status => loop.play;
    }

    status => loop.record;
    status => isRecording;

    return isRecording;
  }

  fun int record() {
    return isRecording;
  }

  fun void clear(int status) {
    if (status) {
      loop.clear();
    }
  }

  fun float volume(float value) {
    value => loopGain.gain;
    return loopGain.gain();
  }

  fun float volume() {
    return loopGain.gain();
  }

  fun float feedback(float value) {
    value => loop.feedback;
    return loop.feedback();
  }

  fun float feedback() {
    return loop.feedback();
  }

  fun float position(float value) {
    value * LOOP_DURATION => loop.playPos;
    return loop.playPos() / LOOP_DURATION;
  }

  fun float position() {
    return loop.playPos() / LOOP_DURATION;
  }

  fun float rate(float value) {
    value * dir => loop.rate;
    return value;
  }

  fun float rate() {
    return loop.rate();
  }

  fun int direction(int value) {
    value => dir;
    dir * Std.fabs(loop.rate()) => loop.rate;
    return value;
  }

  fun int direction() {
    return dir;
  }

  fun void subloop(float a, float b) {
    a * LOOP_DURATION => loop.loopStart;
    b * LOOP_DURATION => loop.loopEnd;
  }

  fun float loopStart() {
    return loop.loopStart() / LOOP_DURATION;
  }

  fun float loopEnd() {
    loop.loopEnd() / LOOP_DURATION => float end;

    if (end > (1.0 - EPS)) {
      return 1.0;
    }


    return end;
  }
}

// main chucks

Gain inputGain, passThrough;

adc => inputGain;
adc => passThrough => dac;

1.0 => inputGain.gain;
1.0 => passThrough.gain;

Loop loop[LOOPS_COUNT];

for (0 => int i; i < LOOPS_COUNT; i++) {
  loop[i].init(inputGain);
  loop[i].feedback(1.0);
  loop[i].volume(1.0);
}

// osc

class OscListener {
  fun void run(string msg, int port) {
    OscIn oscIn;
    OscMsg msg;
    port => oscIn.port;

    oscIn.listenAll();

    while (true) {
      oscIn => now;

      while (oscIn.recv(msg)) {
        if (msg.address.find("/recording") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(1) => int status;

          <<< chan, "record", status >>>;

          loop[chan].record(status);
        }

        else if (msg.address.find("/play") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(1) => int status;

          <<< chan, "play", status >>>;

          loop[chan].play(status);
        }

        else if (msg.address.find("/feedback") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float value;

          <<< chan, "feedback", value >>>;

          loop[chan].feedback(value);
        }

        else if (msg.address.find("/volume") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float value;

          <<< chan, "volume", value >>>;

          loop[chan].volume(value);
        }

        else if (msg.address.find("/clear") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(0) => int status;

          <<< chan, "clear", status >>>;

          loop[chan].clear(status);
        }

        else if (msg.address.find("/jump") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float value;

          <<< chan, "position", value >>>;

          loop[chan].position(value);
        }

        else if (msg.address.find("/rate") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float value;

          <<< chan, "rate", value >>>;

          loop[chan].rate(value);
        }

        else if (msg.address.find("/direction") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(1) => int value;

          <<< chan, "direction", value >>>;

          loop[chan].direction(value);
        }

        else if (msg.address.find("/subloop") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float a;
          msg.getFloat(2) => float b;

          <<< chan, "subloop", a, b >>>;

          loop[chan].subloop(a, b);
        }

        else {
          <<< "unrecognized message: ", msg.address >>>;
        }
      }
    }
  }
}

class OscSender {
  fun void run(string host, int port) {
    OscOut oscOut;
    oscOut.dest(host, port);

    while (true) {
      0.01::second => now;

      for (0 => int i; i < LOOPS_COUNT; i++) {
        oscOut.start("/status/" + i);

        loop[i].play() => oscOut.add;
        loop[i].record() => oscOut.add;
        loop[i].position() => oscOut.add;
        loop[i].volume() => oscOut.add;
        loop[i].feedback() => oscOut.add;
        Std.fabs(loop[i].rate()) => oscOut.add;
        loop[i].direction() => oscOut.add;
        loop[i].loopStart() => oscOut.add;
        loop[i].loopEnd() => oscOut.add;

        oscOut.send();
      }
    }
  }
}


// init

OscListener oscListener;
OscSender oscSender;

spork ~ oscListener.run(HOST, PORT_IN);
spork ~ oscSender.run(HOST, PORT_OUT);

<<< "Nótt Backend Ready" >>>;

while (true) {
  1::second => now;
}
