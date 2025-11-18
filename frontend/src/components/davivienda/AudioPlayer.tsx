import { useRef, useState, useEffect } from 'react';
import { Button } from '../ui/button';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
  Volume1,
  Download,
  Loader2
} from 'lucide-react';

interface AudioPlayerProps {
  audioUrl: string;
  title?: string;
  onTimeUpdate?: (currentTime: number) => void;
}

export function AudioPlayer({ audioUrl, title, onTimeUpdate }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [waveformData, setWaveformData] = useState<number[]>([]);

  useEffect(() => {
    generateWaveform();
  }, [audioUrl]);

  const generateWaveform = () => {
    // Generate a beautiful animated waveform
    const bars = 100;
    const data = Array.from({ length: bars }, (_, i) => {
      // Create a wave pattern
      const position = i / bars;
      const wave = Math.sin(position * Math.PI * 4) * 0.3 + 0.7;
      const randomness = Math.random() * 0.2;
      return wave + randomness;
    });
    setWaveformData(data);
  };

  useEffect(() => {
    if (canvasRef.current && waveformData.length > 0) {
      drawWaveform();
    }
  }, [waveformData, currentTime, duration]);

  const drawWaveform = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const barWidth = width / waveformData.length;
    const progress = duration > 0 ? currentTime / duration : 0;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw waveform bars
    waveformData.forEach((value, index) => {
      const barHeight = value * height * 0.8;
      const x = index * barWidth;
      const y = (height - barHeight) / 2;

      // Determine color based on progress
      const barProgress = index / waveformData.length;
      const isPlayed = barProgress <= progress;

      // Create gradient
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      if (isPlayed) {
        gradient.addColorStop(0, '#E30519');
        gradient.addColorStop(1, '#b00414');
      } else {
        gradient.addColorStop(0, '#e5e7eb');
        gradient.addColorStop(1, '#9ca3af');
      }

      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, barWidth - 1, barHeight);

      // Add glow effect for played section
      if (isPlayed && isPlaying) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#E30519';
        ctx.fillRect(x, y, barWidth - 1, barHeight);
        ctx.shadowBlur = 0;
      }
    });
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const time = audioRef.current.currentTime;
      setCurrentTime(time);
      if (onTimeUpdate) {
        onTimeUpdate(time);
      }
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
      setIsLoading(false);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    setCurrentTime(0);
  };

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!audioRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;

    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const vol = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.volume = vol;
      setVolume(vol);
      setIsMuted(vol === 0);
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      const newMuted = !isMuted;
      audioRef.current.muted = newMuted;
      setIsMuted(newMuted);
    }
  };

  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getVolumeIcon = () => {
    if (isMuted || volume === 0) return VolumeX;
    if (volume < 0.5) return Volume1;
    return Volume2;
  };

  const VolumeIcon = getVolumeIcon();

  return (
    <div className="p-6 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl shadow-2xl">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        preload="metadata"
      />

      {title && (
        <div className="mb-4">
          <h3 className="text-white font-semibold text-lg truncate">{title}</h3>
        </div>
      )}

      {/* Waveform Visualization */}
      <div className="mb-6 relative">
        <canvas
          ref={canvasRef}
          width={800}
          height={100}
          className="w-full h-24 cursor-pointer rounded-lg"
          onClick={handleSeek}
          style={{ imageRendering: 'crisp-edges' }}
        />
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800/50 rounded-lg">
            <Loader2 className="w-8 h-8 text-white animate-spin" />
          </div>
        )}
      </div>

      {/* Time Display */}
      <div className="flex justify-between text-sm text-gray-400 mb-4">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={(e) => {
            const time = parseFloat(e.target.value);
            if (audioRef.current) {
              audioRef.current.currentTime = time;
              setCurrentTime(time);
            }
          }}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider-thumb"
          style={{
            background: `linear-gradient(to right, #E30519 0%, #E30519 ${(currentTime / duration) * 100}%, #374151 ${(currentTime / duration) * 100}%, #374151 100%)`
          }}
        />
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            onClick={() => skip(-10)}
            disabled={isLoading}
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/10"
          >
            <SkipBack className="w-5 h-5" />
          </Button>

          <Button
            onClick={togglePlay}
            disabled={isLoading}
            size="lg"
            className="bg-gradient-to-r from-[#E30519] to-red-600 hover:from-red-600 hover:to-[#E30519] text-white w-14 h-14 rounded-full shadow-lg hover:shadow-xl transition-all"
          >
            {isPlaying ? (
              <Pause className="w-6 h-6" fill="white" />
            ) : (
              <Play className="w-6 h-6 ml-1" fill="white" />
            )}
          </Button>

          <Button
            onClick={() => skip(10)}
            disabled={isLoading}
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/10"
          >
            <SkipForward className="w-5 h-5" />
          </Button>
        </div>

        {/* Volume Control */}
        <div className="flex items-center gap-3">
          <Button
            onClick={toggleMute}
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/10"
          >
            <VolumeIcon className="w-5 h-5" />
          </Button>

          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-24 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer slider-thumb"
            style={{
              background: `linear-gradient(to right, #E30519 0%, #E30519 ${volume * 100}%, #374151 ${volume * 100}%, #374151 100%)`
            }}
          />

          <a
            href={audioUrl}
            download
            className="ml-2"
          >
            <Button
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/10"
            >
              <Download className="w-5 h-5" />
            </Button>
          </a>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{
        __html: `
          .slider-thumb::-webkit-slider-thumb {
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #E30519;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(227, 5, 25, 0.5);
          }

          .slider-thumb::-moz-range-thumb {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #E30519;
            cursor: pointer;
            border: none;
            box-shadow: 0 0 10px rgba(227, 5, 25, 0.5);
          }
        `
      }} />
    </div>
  );
}
