class Loop {
  LiSa loop;
  Gain loopGain;

  fun void init(Gain input) {
    8::second => loop.duration;

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
}

class OscListener {
  function void listenOnOsc(string msg, int port) {
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

  function void receiveEvent(OscEvent event) {}
}

Gain inputGain, passThrough;

adc => inputGain;
8   => int LOOPS_COUNT;

adc => passThrough => dac;

1.0 => inputGain.gain;
1.0 => passThrough.gain;

Loop loop[LOOPS_COUNT];

for (0 => int i; i < LOOPS_COUNT; i++) {
  loop[i].init(inputGain);
  loop[i].feedback(1.0);
  loop[i].volume(1.0);
}

class ListenRecording extends OscListener {
  function void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getInt() => int status;

    <<< chan, "record", status >>>;

    loop[chan].record(status);
  }
}

class ListenPlaying extends OscListener {
  function void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getInt() => int status;

    <<< chan, "play", status >>>;

    loop[chan].play(status);
  }
}

class ListenFeedback extends OscListener {
  function void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getFloat() => float value;

    <<< chan, "feedback", value >>>;

    loop[chan].feedback(value);
  }
}

class ListenVolume extends OscListener {
  function void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getFloat() => float value;

    <<< chan, "volume", value >>>;

    loop[chan].volume(value);
  }
}

class ListenClear extends OscListener {
  function void receiveEvent(OscEvent event) {
    event.getInt() => int chan;
    event.getInt() => int status;

    <<< chan, "clear", status >>>;

    loop[chan].clear(status);
  }
}

ListenRecording listenRecording;
ListenPlaying listenPlaying;
ListenFeedback listenFeedback;
ListenVolume listenVolume;
ListenClear listenClear;

spork ~ listenRecording.listenOnOsc("/recording, i i", 3000);
spork ~ listenPlaying.listenOnOsc("/playing, i i", 3000);
spork ~ listenFeedback.listenOnOsc("/feedback, i f", 3000);
spork ~ listenVolume.listenOnOsc("/volume, i f", 3000);
spork ~ listenClear.listenOnOsc("/clear, i i", 3000);

<<< "Nótt Backend Ready" >>>;

while (true) {
  1::second => now;
}
