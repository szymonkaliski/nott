// globals

"localhost" => string HOST;
3001        => int PORT_OUT;
3000        => int PORT_IN;
8           => int LOOPS_COUNT;
6::second   => dur LOOP_DURATION;

// loops

class Loop {
  LiSa loop;
  Gain loopGain;

  fun void init(Gain input) {
    LOOP_DURATION => loop.duration;

    1 => loop.loop;
    1 => loop.loopRec;
    1 => loop.maxVoices;

    // -1.0 => loop.rate; // works!

    input => loop => loopGain => dac;
  }

  fun void play(int status) {
    status => loop.play;
  }

  fun void record(int status) {
    if (status) {
      loop.playPos() => loop.recPos;
      status => loop.play;
    }

    status => loop.record;
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
      0.1::second => now;

      for (0 => int i; i < LOOPS_COUNT; i++) {
        oscOut.start("/status/" + i);
        loop[i].position() => oscOut.add;
        loop[i].volume() => oscOut.add;
        loop[i].feedback() => oscOut.add;
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
