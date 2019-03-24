// globals

"localhost" => string HOST;
3001        => int PORT_OUT;
3000        => int PORT_IN;
6           => int LOOPS_COUNT;
8::second   => dur LOOP_DURATION;
// 4::second   => dur LOOP_DURATION;
0.01        => float EPS;

"MODE_STANDARD" => string MODE_STANDARD;
"MODE_GRANULAR" => string MODE_GRANULAR;

fun float clamp(float v, float a, float b) {
  return Math.min(b, Math.max(v, a));
}

// loops

class Loop {
  LiSa loop;
  Gain loopGain;
  int dir;

  int isPlaying;
  int isRecording;

  string currentMode;

  float granularSpan;
  float granularLength;
  int granularVoices;
  int granularDirection; // 1 fwd, 2 bkwd, 3 rand
  int granularRepitch; // 1 on, 0 off

  fun void init(Gain input) {
    LOOP_DURATION => loop.duration;

    1 => dir;
    MODE_STANDARD => mode;

    1 => loop.loop;
    1 => loop.loopRec;
    16 => loop.maxVoices;

    1.0 / 64.0 => granularSpan;
    1.0 / 64.0 => granularLength;
    4 => granularVoices;
    3 => granularDirection;
    0 => granularRepitch;

    input => loop => loopGain => dac;

    spork ~ run();
  }

  fun void run() {
    while (true) {
      if (currentMode == MODE_STANDARD) {
        // nothing
      }

      if (currentMode == MODE_GRANULAR) {
        spork ~ grain();
      }

      1::ms => now;
    }
  }

  fun void grain() {
    // voice 0 plays through file normally, pointing to where we are

    loop.getVoice() => int newVoice;
    loop.playPos() / LOOP_DURATION => float pos;

    LOOP_DURATION * granularLength => dur grainLength;
    (grainLength / 4.0) => dur rampTime;

    1 => int grainDir;

    if (granularDirection == 2) {
      -1 => grainDir;
    }

    if (granularDirection == 3) {
      Std.rand2f(0.0, 1.0) >= 0.5 ? 1 : -1 => grainDir;
    }

    1.0 => float grainRate;

    if (granularRepitch == 1) {
      Std.fabs(loop.rate()) => grainRate;
    }

    if (newVoice >= 1 && newVoice - 1 <= granularVoices && isPlaying == 1) {
      clamp(pos + Std.rand2f(-granularSpan, granularSpan), 0.0, 1.0) => float randomPos;

      loop.rate(newVoice, grainDir * grainRate);
      loop.voiceGain(newVoice, 1.0 - 1.0 / (18.0 - granularVoices));
      loop.playPos(newVoice, randomPos * LOOP_DURATION);
      loop.rampUp(newVoice, rampTime);

      (grainLength - rampTime * 2.0) => now;

      loop.rampDown(newVoice, rampTime);

      rampTime => now;
    }
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
    if (status == 1) {
      loop.playPos() => loop.recPos;
      play(1);
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
    // loop playback
    a * LOOP_DURATION => loop.loopStart;
    b * LOOP_DURATION => loop.loopEnd;

    // loop recording, loop record start position is handled by loopStart
    b * LOOP_DURATION => loop.loopEndRec;
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

  fun string mode(string newMode) {
    if (newMode != currentMode) {
      if (newMode == MODE_GRANULAR) {
        loop.voiceGain(0, 0.0);
      }

      if (newMode == MODE_STANDARD) {
        loop.voiceGain(0, 1.0);
      }
    }

    newMode => currentMode;
    return currentMode;
  }

  fun string mode() {
    return currentMode;
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

        else if (msg.address.find("/mode") == 0) {
          msg.getInt(0) => int chan;
          msg.getString(1) => string newMode;

          <<< chan, "playback mode", newMode >>>;

          loop[chan].mode(newMode);
        }

        else if (msg.address.find("/granular_span") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float granularSpan;

          <<< chan, "granular span", granularSpan >>>;

          granularSpan => loop[chan].granularSpan;
        }

        else if (msg.address.find("/granular_length") == 0) {
          msg.getInt(0) => int chan;
          msg.getFloat(1) => float granularLength;

          <<< chan, "granular length", granularLength >>>;

          granularLength => loop[chan].granularLength;
        }

        else if (msg.address.find("/granular_voices") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(1) => int granularVoices;

          <<< chan, "granular voices", granularVoices >>>;

          granularVoices => loop[chan].granularVoices;
        }

        else if (msg.address.find("/granular_direction") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(1) => int granularDirection;

          <<< chan, "granular direction", granularDirection >>>;

          granularDirection => loop[chan].granularDirection;
        }

        else if (msg.address.find("/granular_repitch") == 0) {
          msg.getInt(0) => int chan;
          msg.getInt(1) => int granularRepitch;

          <<< chan, "granular repitch", granularRepitch >>>;

          granularRepitch => loop[chan].granularRepitch;
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

        loop[i].mode() => oscOut.add;
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

        if (loop[i].mode() == MODE_GRANULAR) {
          oscOut.start("/status_granular/" + i);

          loop[i].granularSpan => oscOut.add;
          loop[i].granularLength => oscOut.add;
          loop[i].granularVoices => oscOut.add;
          loop[i].granularDirection => oscOut.add;
          loop[i].granularRepitch => oscOut.add;

          oscOut.send();
        }
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
