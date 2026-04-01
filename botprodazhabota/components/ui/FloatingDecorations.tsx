import styles from '@/styles/decorations.module.scss';

const Molecule = () => (
  <svg viewBox="0 0 72 72" fill="none" width="58" height="58" aria-hidden="true">
    <circle cx="36" cy="10" r="7" stroke="#8899CC" strokeWidth="1.4" fill="rgba(255,255,255,.65)" />
    <circle cx="11" cy="55" r="7" stroke="#8899CC" strokeWidth="1.4" fill="rgba(255,255,255,.65)" />
    <circle cx="61" cy="55" r="7" stroke="#8899CC" strokeWidth="1.4" fill="rgba(255,255,255,.65)" />
    <circle cx="36" cy="38" r="5" stroke="#8899CC" strokeWidth="1.2" fill="rgba(255,255,255,.65)" />
    <line x1="36" y1="17" x2="36" y2="33" stroke="#AABBDD" strokeWidth="1.1" strokeDasharray="3 2.4"/>
    <line x1="17" y1="51" x2="31" y2="42" stroke="#AABBDD" strokeWidth="1.1" strokeDasharray="3 2.4"/>
    <line x1="55" y1="51" x2="41" y2="42" stroke="#AABBDD" strokeWidth="1.1" strokeDasharray="3 2.4"/>
    <line x1="18" y1="56" x2="54" y2="56" stroke="#AABBDD" strokeWidth="1.1" strokeDasharray="3 2.4"/>
  </svg>
);

const VKIcon = () => (
  <svg width="26" height="26" viewBox="0 0 32 32" fill="none" aria-hidden="true">
    <rect width="32" height="32" rx="8" fill="#3D6FBB" fillOpacity=".12"/>
    <path d="M17.1 21.5C11 21.5 7.5 17.2 7.4 10H10.5c.1 5.3 2.4 7.5 4.2 7.9V10H17.6v4.5c1.8-.2 3.7-2.3 4.3-4.5h2.9c-.5 2.8-2.5 4.9-4 5.8 1.4.7 3.7 2.5 4.5 5.7h-3.2c-.7-2.1-2.4-3.7-4.6-4V21.5h-.4z" fill="#3D6FBB"/>
  </svg>
);

const Gear = ({ size = 52 }: { size?: number }) => (
  <svg viewBox="0 0 52 52" fill="none" width={size} height={size} aria-hidden="true">
    <circle cx="26" cy="26" r="7.5" stroke="#9AAABB" strokeWidth="1.5" fill="rgba(255,255,255,.35)"/>
    <circle cx="26" cy="26" r="3.2" fill="#9AAABB" fillOpacity=".55"/>
    <path d="M40.2 28.8l2.6-2.1a1.5 1.5 0 00.3-2l-2.3-4a1.5 1.5 0 00-1.9-.5l-3 1.3c-.8-.5-1.7-1-2.6-1.4l-.5-3.2a1.5 1.5 0 00-1.5-1.2h-4.6a1.5 1.5 0 00-1.5 1.2l-.5 3.2c-1 .4-1.8.9-2.6 1.4l-3-1.3a1.5 1.5 0 00-1.9.5l-2.3 4a1.5 1.5 0 00.3 2l2.6 2.1c0 .4-.1.8-.1 1.2s0 .8.1 1.2l-2.6 2.1a1.5 1.5 0 00-.3 2l2.3 4c.4.7 1.3.9 1.9.5l3-1.3c.8.5 1.7 1 2.6 1.4l.5 3.2c.2.7.8 1.2 1.5 1.2h4.6c.7 0 1.3-.5 1.5-1.2l.5-3.2c1-.4 1.8-.9 2.6-1.4l3 1.3c.7.4 1.5.2 1.9-.5l2.3-4a1.5 1.5 0 00-.3-2l-2.6-2.1c0-.4.1-.8.1-1.2s0-.8-.1-1.2z"
      stroke="#9AAABB" strokeWidth="1.3" fill="none"/>
  </svg>
);

export function LeftDecorations() {
  return (
    <div className={styles.left} aria-hidden="true">
      <div className={styles.ghostLeft} />
      <div className={styles.moleculeCard}><Molecule /></div>
      <div className={styles.vkCard}>
        <div className={styles.badgeRow}>
          <VKIcon />
          <div className={styles.badgeText}>
            <span className={styles.badgeName}>ВКонтакте</span>
            <span className={styles.badgeSub}>Автоматизация</span>
          </div>
        </div>
      </div>
      <div className={styles.dot} style={{width:11,height:11,top:'26%',right:'-12px'}}/>
      <div className={styles.dot} style={{width:7, height:7, top:'52%',left:'10px',animationDelay:'1.1s'}}/>
      <div className={styles.dot} style={{width:13,height:13,bottom:'22%',right:'-5px',animationDelay:'.6s'}}/>
    </div>
  );
}

export function RightDecorations() {
  return (
    <div className={styles.right} aria-hidden="true">
      <div className={styles.ghostRight} />
      <div className={styles.gearBig}>
        <div className={styles.gearSpin}><Gear size={52}/></div>
      </div>
      <div className={styles.aiCard}>
        <div className={styles.aiAvatar}>AI</div>
        <div className={styles.aiText}>
          <span className={styles.aiName}>Нейросеть</span>
          <span className={styles.aiStatus}>GPT-4o · активен</span>
        </div>
      </div>
      <div className={styles.orb}/>
      <div className={styles.gearSmall}><Gear size={34}/></div>
      <div className={styles.dot} style={{width:9, height:9, top:'18%',left:'-10px'}}/>
      <div className={styles.dot} style={{width:12,height:12,bottom:'26%',right:'12px',animationDelay:'.9s'}}/>
    </div>
  );
}
