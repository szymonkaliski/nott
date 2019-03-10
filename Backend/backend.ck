// globals

"localhost" => string HOST;
3001        => int PORT_OUT;
3000        => int PORT_IN;
8           => int LOOPS_COUNT;
8::second   => dur LOOP_DURATION;

// loops

class Loop {
  LiSa loop;
  Gain loopGain;

  fun void init(Gain input) {
    LOOP_DURATION => loop.duration;

    1 => loop.loop;
    1 => loop.loopRec;
    1 => loop.maxVoices;

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

  fun void volume(float value) {
    value => loopGain.gain;
  }

  fun void feedback(float value) {
    value => loop.feedback;
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
  fun void listenOnOsc(string msg, int port) {
    OscRecv recv;
    port => recv.port;

    recv.listen();
    recv.event(msg) @=> OscEvent event;

    while (true) {
      event => now;

      while (event.nextMsg()) {
        receiveEvent(event);
      }
    }
  }

  fun void receiveEvent(OscEvent event) {}
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
        oscOut.send();
      }
    }
  }
}

class ListenRecording extends OscListener {
  fun void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getInt() => int status;

    <<< chan, "record", status >>>;

    loop[chan].record(status);
  }
}

class ListenPlaying extends OscListener {
  fun void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getInt() => int status;

    <<< chan, "play", status >>>;

    loop[chan].play(status);
  }
}

class ListenFeedback extends OscListener {
  fun void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getFloat() => float value;

    <<< chan, "feedback", value >>>;

    loop[chan].feedback(value);
  }
}

class ListenVolume extends OscListener {
  fun void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getFloat() => float value;

    <<< chan, "volume", value >>>;

    loop[chan].volume(value);
  }
}

class ListenClear extends OscListener {
  fun void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getInt() => int status;

    <<< chan, "clear", status >>>;

    loop[chan].clear(status);
  }
}

// init

ListenRecording listenRecording;
ListenPlaying listenPlaying;
ListenFeedback listenFeedback;
ListenVolume listenVolume;
ListenClear listenClear;

spork ~ listenRecording.listenOnOsc("/recording, i i", PORT_IN);
spork ~ listenPlaying.listenOnOsc("/playing, i i", PORT_IN);
spork ~ listenFeedback.listenOnOsc("/feedback, i f", PORT_IN);
spork ~ listenVolume.listenOnOsc("/volume, i f", PORT_IN);
spork ~ listenClear.listenOnOsc("/clear, i i", PORT_IN);

OscSender oscSender;

spork ~ oscSender.run(HOST, PORT_OUT);

<<< "Nótt Backend Ready" >>>;

while (true) {
  1::second => now;
}
