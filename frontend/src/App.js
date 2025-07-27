import React, { useState, useEffect } from 'react';
import './App.css';

const FuturisticHero = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    setIsLoaded(true);
    
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="futuristic-hero">
      {/* Animated Background with Particles */}
      <div className="hero-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
        
        {/* Floating Particles */}
        <div className="particles-container">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 10}s`,
                animationDuration: `${10 + Math.random() * 20}s`
              }}
            />
          ))}
        </div>

        {/* Geometric Shapes */}
        <div className="geometric-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
          <div className="shape shape-5"></div>
        </div>

        {/* Grid Pattern */}
        <div className="grid-pattern"></div>
        
        {/* Dynamic Mouse Light */}
        <div 
          className="mouse-light"
          style={{
            left: `${mousePosition.x}%`,
            top: `${mousePosition.y}%`
          }}
        ></div>
      </div>

      {/* Main Content */}
      <div className="hero-content">
        <div className="content-wrapper">
          {/* Animated Title */}
          <div className={`hero-title ${isLoaded ? 'animate-in' : ''}`}>
            <h1 className="main-title">
              <span className="title-line">
                <span className="letter-animation">T</span>
                <span className="letter-animation">H</span>
                <span className="letter-animation">E</span>
                <span className="spacer"></span>
                <span className="letter-animation">F</span>
                <span className="letter-animation">U</span>
                <span className="letter-animation">T</span>
                <span className="letter-animation">U</span>
                <span className="letter-animation">R</span>
                <span className="letter-animation">E</span>
              </span>
              <span className="title-line gradient-text">
                <span className="letter-animation">I</span>
                <span className="letter-animation">S</span>
                <span className="spacer"></span>
                <span className="letter-animation">N</span>
                <span className="letter-animation">O</span>
                <span className="letter-animation">W</span>
              </span>
            </h1>
            
            <div className="title-decoration">
              <div className="decoration-line line-1"></div>
              <div className="decoration-circle"></div>
              <div className="decoration-line line-2"></div>
            </div>
          </div>

          {/* Animated Subtitle */}
          <div className={`hero-subtitle ${isLoaded ? 'animate-in' : ''}`}>
            <p className="subtitle-text">
              Experience the next generation of digital innovation.
              <br />
              <span className="highlight-text">Revolutionize your vision with cutting-edge technology.</span>
            </p>
          </div>

          {/* Holographic Cards */}
          <div className={`hero-cards ${isLoaded ? 'animate-in' : ''}`}>
            <div className="holo-card card-1">
              <div className="card-glow"></div>
              <div className="card-content">
                <div className="card-icon">⚡</div>
                <h3>Lightning Fast</h3>
                <p>Ultra-responsive performance</p>
              </div>
            </div>
            
            <div className="holo-card card-2">
              <div className="card-glow"></div>
              <div className="card-content">
                <div className="card-icon">🚀</div>
                <h3>Next-Gen Tech</h3>
                <p>Powered by innovation</p>
              </div>
            </div>
            
            <div className="holo-card card-3">
              <div className="card-glow"></div>
              <div className="card-content">
                <div className="card-icon">✨</div>
                <h3>Seamless UX</h3>
                <p>Intuitive and beautiful</p>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className={`hero-actions ${isLoaded ? 'animate-in' : ''}`}>
            <button className="cta-button primary-cta">
              <span className="button-text">Get Started</span>
              <div className="button-glow"></div>
              <div className="button-particles">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="button-particle"></div>
                ))}
              </div>
            </button>
            
            <button className="cta-button secondary-cta">
              <span className="button-text">Learn More</span>
              <div className="button-border"></div>
            </button>
          </div>

          {/* Floating Stats */}
          <div className={`floating-stats ${isLoaded ? 'animate-in' : ''}`}>
            <div className="stat-item">
              <div className="stat-number" data-target="10000">0</div>
              <div className="stat-label">Active Users</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number" data-target="99.9">0</div>
              <div className="stat-label">Uptime %</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number" data-target="24">0</div>
              <div className="stat-label">Support 24/7</div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="scroll-indicator">
          <div className="scroll-wheel">
            <div className="scroll-dot"></div>
          </div>
          <span className="scroll-text">Scroll to explore</span>
        </div>
      </div>

      {/* Floating Elements */}
      <div className="floating-elements">
        <div className="floating-element element-1">
          <div className="element-inner"></div>
        </div>
        <div className="floating-element element-2">
          <div className="element-inner"></div>
        </div>
        <div className="floating-element element-3">
          <div className="element-inner"></div>
        </div>
      </div>

      {/* Code Rain Effect */}
      <div className="code-rain">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="code-column"
            style={{
              left: `${i * 5}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${8 + Math.random() * 4}s`
            }}
          >
            {['01', '11', '00', '10', '01', '11', '00', '10'].map((code, j) => (
              <span key={j} className="code-char">{code}</span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

const ModernSection = () => (
  <section className="modern-section">
    <div className="section-container">
      <h2 className="section-title">Built for the Future</h2>
      <div className="feature-grid">
        <div className="feature-card">
          <div className="feature-icon">🎯</div>
          <h3>Precision Engineering</h3>
          <p>Every pixel crafted with meticulous attention to detail</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">⚡</div>
          <h3>Blazing Performance</h3>
          <p>Optimized for speed and efficiency across all devices</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🛡️</div>
          <h3>Enterprise Security</h3>
          <p>Military-grade protection for your data and privacy</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🌐</div>
          <h3>Global Scale</h3>
          <p>Built to handle millions of users worldwide</p>
        </div>
      </div>
    </div>
  </section>
);

function App() {
  useEffect(() => {
    // Counter animation for stats
    const animateCounters = () => {
      const counters = document.querySelectorAll('.stat-number');
      counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const increment = target / 100;
        let current = 0;
        
        const updateCounter = () => {
          if (current < target) {
            current += increment;
            counter.textContent = Math.ceil(current);
            setTimeout(updateCounter, 20);
          } else {
            counter.textContent = target + (target === 99.9 ? '' : '+');
          }
        };
        
        setTimeout(updateCounter, 2000);
      });
    };

    // Start animations
    setTimeout(animateCounters, 3000);
  }, []);

  return (
    <div className="App">
      <FuturisticHero />
      <ModernSection />
    </div>
  );
}

export default App;