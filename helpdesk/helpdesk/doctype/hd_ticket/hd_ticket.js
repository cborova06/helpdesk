// Copyright (c) 2023, Frappe Technologies and contributors
// For license information, please see license.txt

// Liste görünümü için formatters
frappe.listview_settings['HD Ticket'] = {
  add_fields: ["last_sentiment", "sentiment_trend", "effort_score", "effort_band"],
  
  formatters: {
    last_sentiment: function(value) {
      if (!value) return '';
      
      // Normalize value - support both English and Turkish
      const normalized = value.toLowerCase().trim();
      let config;
      
      if (normalized.includes('olumlu') || normalized.includes('positive')) {
        config = { emoji: '😊', color: '#28a745', bg: '#d4edda', label: __('Olumlu') };
      } else if (normalized.includes('nötr') || normalized.includes('neutral') || normalized.includes('nautral')) {
        config = { emoji: '😐', color: '#856404', bg: '#fff3cd', label: __('Nötr') };
      } else if (normalized.includes('olumsuz') || normalized.includes('negative')) {
        config = { emoji: '😟', color: '#721c24', bg: '#f8d7da', label: __('Olumsuz') };
      } else {
        config = { emoji: '❓', color: '#6c757d', bg: '#e9ecef', label: value };
      }
      
      return `<span style="background-color: ${config.bg}; color: ${config.color}; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.85em; white-space: nowrap; display: inline-block;">
        ${config.emoji} ${config.label}
      </span>`;
    },
    
    sentiment_trend: function(value) {
      if (!value) return '';
      const trend_lower = value.toLowerCase().trim();
      let config;
      
      if (trend_lower.includes('improv') || trend_lower.includes('yüksel') || trend_lower.includes('↑') || trend_lower.includes('iyileş')) {
        config = { emoji: '📈', color: '#28a745', bg: '#d4edda', label: __('İyileşiyor') };
      } else if (trend_lower.includes('declin') || trend_lower.includes('düş') || trend_lower.includes('↓') || trend_lower.includes('kötü')) {
        config = { emoji: '📉', color: '#dc3545', bg: '#f8d7da', label: __('Kötüleşiyor') };
      } else if (trend_lower.includes('stabil') || trend_lower.includes('stabl') || trend_lower.includes('sabit') || trend_lower.includes('→')) {
        config = { emoji: '➡️', color: '#007bff', bg: '#cfe2ff', label: __('Stabil') };
      } else if (trend_lower.includes('volat') || trend_lower.includes('dalgal') || trend_lower.includes('↕')) {
        config = { emoji: '〰️', color: '#ffc107', bg: '#fff3cd', label: __('Değişken') };
      } else {
        config = { emoji: '📊', color: '#6c757d', bg: '#e9ecef', label: value };
      }
      
      return `<span style="background-color: ${config.bg}; color: ${config.color}; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.85em; white-space: nowrap; display: inline-block;">
        ${config.emoji} ${config.label}
      </span>`;
    },
    
    effort_score: function(value) {
      if (value === null || value === undefined || value === '') return '';
      const score = parseFloat(value);
      if (isNaN(score)) return value;
      
      let config;
      if (score <= 29) {
        config = { color: '#28a745', bg: '#d4edda', indicator: '🟢' };
      } else if (score <= 49) {
        config = { color: '#5cb85c', bg: '#d4edda', indicator: '🟡' };
      } else if (score <= 69) {
        config = { color: '#ffc107', bg: '#fff3cd', indicator: '🟠' };
      } else if (score <= 89) {
        config = { color: '#dc3545', bg: '#f8d7da', indicator: '🔴' };
      } else {
        config = { color: '#c82333', bg: '#f5c6cb', indicator: '🔴🔴' };
      }
      
      return `<span style="background-color: ${config.bg}; color: ${config.color}; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85em; white-space: nowrap; display: inline-block;">
        ${config.indicator} ${score.toFixed(1)}
      </span>`;
    },
    
    effort_band: function(value) {
      if (!value) return '';
      
      // Normalize value - support both English and Turkish
      const normalized = value.toLowerCase().trim();
      let config;
      
      if (normalized.includes('düşük') || normalized.includes('low') || normalized.includes('düsük')) {
        config = { emoji: '✅', color: '#28a745', bg: '#d4edda', label: __('Düşük') };
      } else if (normalized.includes('orta') || normalized.includes('medium') || normalized.includes('moderate')) {
        config = { emoji: '⚠️', color: '#ffc107', bg: '#fff3cd', label: __('Orta') };
      } else if (normalized.includes('yüksek') || normalized.includes('high') || normalized.includes('yuksek')) {
        config = { emoji: '🔴', color: '#dc3545', bg: '#f8d7da', label: __('Yüksek') };
      } else {
        config = { emoji: '❓', color: '#6c757d', bg: '#e9ecef', label: value };
      }
      
      return `<span style="background-color: ${config.bg}; color: ${config.color}; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.85em; white-space: nowrap; display: inline-block;">
        ${config.emoji} ${config.label}
      </span>`;
    }
  },
  
  onload: function(listview) {
    console.log('HD Ticket listview loaded with formatters');
  }
};

frappe.ui.form.on("HD Ticket", {
  onload(frm) {
    if (frm.is_new()) return;
    frm.call("mark_seen");
  },
  
  refresh(frm) {
    // AI Insight alanlarını özelleştir
    setTimeout(() => {
      render_ai_fields_as_badges(frm);
      expand_sidebar_fields(frm);
    }, 200);
  },
  
  last_sentiment(frm) {
    setTimeout(() => enhance_sentiment_field(frm), 50);
  },
  
  effort_score(frm) {
    setTimeout(() => enhance_effort_score_field(frm), 50);
  },
  
  effort_band(frm) {
    setTimeout(() => enhance_effort_band_field(frm), 50);
  },
  
  sentiment_trend(frm) {
    setTimeout(() => enhance_sentiment_trend_field(frm), 50);
  }
});

// Sentiment alanına emoji ve renk ekle
function enhance_sentiment_field(frm) {
  const sentiment = frm.doc.last_sentiment;
  if (!sentiment) return;
  
  const sentiment_config = {
    'Positive': { emoji: '😊', color: '#d4edda', border: '#c3e6cb', text: '#155724' },
    'Nautral': { emoji: '😐', color: '#fff3cd', border: '#ffeaa7', text: '#856404' },
    'Neutral': { emoji: '😐', color: '#fff3cd', border: '#ffeaa7', text: '#856404' },
    'Negative': { emoji: '😟', color: '#f8d7da', border: '#f5c6cb', text: '#721c24' }
  };
  
  const config = sentiment_config[sentiment];
  if (!config) return;
  
  // Sentiment field wrapper'ı bul ve stil ekle
  const field = frm.fields_dict.last_sentiment;
  if (field && field.$wrapper) {
    const $input = field.$wrapper.find('select, input');
    const $wrapper = field.$wrapper.find('.control-input-wrapper');
    
    if ($wrapper.length) {
      $wrapper.css({
        'background-color': config.color,
        'border': `2px solid ${config.border}`,
        'border-radius': '8px',
        'padding': '8px',
        'transition': 'all 0.3s ease'
      });
    }
    
    // Emoji ekle (eğer yoksa)
    if (!field.$wrapper.find('.sentiment-emoji').length) {
      const $label = field.$wrapper.find('.control-label');
      $label.append(`<span class="sentiment-emoji" style="margin-left: 8px; font-size: 1.2em;">${config.emoji}</span>`);
    } else {
      field.$wrapper.find('.sentiment-emoji').text(config.emoji);
    }
  }
}

// Effort Score alanına dinamik renk gradyanı ekle
function enhance_effort_score_field(frm) {
  const score = frm.doc.effort_score;
  if (score === null || score === undefined) return;
  
  // 0-100 arası skoru renge çevir (yeşilden kırmızıya)
  const color = get_effort_color(score);
  const bg_color = get_effort_background(score);
  
  const field = frm.fields_dict.effort_score;
  if (field && field.$wrapper) {
    const $wrapper = field.$wrapper.find('.control-input-wrapper');
    const $input = field.$wrapper.find('input');
    
    if ($wrapper.length) {
      $wrapper.css({
        'background': bg_color,
        'border-radius': '8px',
        'padding': '8px',
        'border': `2px solid ${color}`,
        'transition': 'all 0.3s ease',
        'box-shadow': `0 2px 4px ${color}30`
      });
      
      $input.css({
        'color': color,
        'font-weight': 'bold',
        'font-size': '1.1em'
      });
    }
    
    // Skor göstergesini label'a ekle
    const $label = field.$wrapper.find('.control-label');
    if (!field.$wrapper.find('.score-indicator').length) {
      const indicator = get_effort_indicator(score);
      $label.append(`<span class="score-indicator" style="margin-left: 8px; font-size: 0.9em; color: ${color};">${indicator}</span>`);
    } else {
      const indicator = get_effort_indicator(score);
      field.$wrapper.find('.score-indicator').html(indicator).css('color', color);
    }
  }
}

// Sentiment Trend alanını güzelleştir
function enhance_sentiment_trend_field(frm) {
  const trend = frm.doc.sentiment_trend;
  if (!trend) return;
  
  // Trend pattern'lerini analiz et (örn: "↑", "↓", "→", "Stable", "Improving", "Declining")
  const trend_analysis = analyze_sentiment_trend(trend);
  
  const field = frm.fields_dict.sentiment_trend;
  if (field && field.$wrapper) {
    const $wrapper = field.$wrapper.find('.control-input-wrapper');
    const $input = field.$wrapper.find('input');
    
    if ($wrapper.length) {
      $wrapper.css({
        'background': trend_analysis.gradient,
        'border': `2px solid ${trend_analysis.border}`,
        'border-radius': '8px',
        'padding': '8px',
        'transition': 'all 0.3s ease',
        'box-shadow': `0 2px 4px ${trend_analysis.color}30`
      });
      
      $input.css({
        'color': trend_analysis.color,
        'font-weight': '600',
        'font-size': '1.05em'
      });
    }
    
    // Trend göstergesini label'a ekle
    const $label = field.$wrapper.find('.control-label');
    if (!field.$wrapper.find('.trend-indicator').length) {
      $label.append(`<span class="trend-indicator" style="margin-left: 8px; font-size: 1.2em;">${trend_analysis.emoji}</span>`);
      $label.append(`<span class="trend-label" style="margin-left: 6px; font-size: 0.85em; color: ${trend_analysis.color}; font-weight: 600;">${trend_analysis.label}</span>`);
    } else {
      field.$wrapper.find('.trend-indicator').text(trend_analysis.emoji);
      field.$wrapper.find('.trend-label').html(trend_analysis.label).css('color', trend_analysis.color);
    }
  }
}

// Sentiment trend analiz fonksiyonu
function analyze_sentiment_trend(trend) {
  const trend_lower = (trend || '').toLowerCase().trim();
  
  // İyileşme pattern'leri
  if (trend_lower.includes('improv') || trend_lower.includes('yüksel') || 
      trend_lower.includes('↑') || trend_lower.includes('better') ||
      trend_lower.includes('pozitif') || trend_lower.includes('iyileş')) {
    return {
      emoji: '📈',
      color: '#28a745',
      gradient: 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
      border: '#28a745',
      label: __('İyileşiyor')
    };
  }
  
  // Kötüleşme pattern'leri
  if (trend_lower.includes('declin') || trend_lower.includes('düş') || 
      trend_lower.includes('↓') || trend_lower.includes('worse') ||
      trend_lower.includes('negatif') || trend_lower.includes('kötü')) {
    return {
      emoji: '📉',
      color: '#dc3545',
      gradient: 'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)',
      border: '#dc3545',
      label: __('Kötüleşiyor')
    };
  }
  
  // Stabil/Sabit pattern'leri
  if (trend_lower.includes('stabl') || trend_lower.includes('sabit') || 
      trend_lower.includes('→') || trend_lower.includes('steady') ||
      trend_lower.includes('değişmiyor') || trend_lower.includes('consistent')) {
    return {
      emoji: '➡️',
      color: '#007bff',
      gradient: 'linear-gradient(135deg, #cfe2ff 0%, #b6d4fe 100%)',
      border: '#007bff',
      label: __('Stabil')
    };
  }
  
  // Dalgalı/Volatil pattern'leri
  if (trend_lower.includes('volat') || trend_lower.includes('dalgal') || 
      trend_lower.includes('↕') || trend_lower.includes('mixed') ||
      trend_lower.includes('karışık') || trend_lower.includes('değişken')) {
    return {
      emoji: '〰️',
      color: '#ffc107',
      gradient: 'linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%)',
      border: '#ffc107',
      label: __('Değişken')
    };
  }
  
  // Varsayılan (neutral)
  return {
    emoji: '📊',
    color: '#6c757d',
    gradient: 'linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%)',
    border: '#6c757d',
    label: __('Analiz Ediliyor')
  };
}

// Effort Band alanını renklendir
function enhance_effort_band_field(frm) {
  const band = frm.doc.effort_band;
  if (!band) return;
  
  const band_config = {
    'Low': { 
      emoji: '✅', 
      color: '#28a745', 
      bg: 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
      border: '#c3e6cb',
      label: __('Düşük Efor')
    },
    'Medium': { 
      emoji: '⚠️', 
      color: '#ffc107', 
      bg: 'linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)',
      border: '#ffeaa7',
      label: __('Orta Efor')
    },
    'High': { 
      emoji: '🔴', 
      color: '#dc3545', 
      bg: 'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)',
      border: '#f5c6cb',
      label: __('Yüksek Efor')
    }
  };
  
  const config = band_config[band];
  if (!config) return;
  
  const field = frm.fields_dict.effort_band;
  if (field && field.$wrapper) {
    const $wrapper = field.$wrapper.find('.control-input-wrapper');
    
    if ($wrapper.length) {
      $wrapper.css({
        'background': config.bg,
        'border': `2px solid ${config.border}`,
        'border-radius': '8px',
        'padding': '8px',
        'transition': 'all 0.3s ease',
        'box-shadow': `0 2px 4px ${config.color}30`
      });
    }
    
    // Emoji ve label ekle
    const $label = field.$wrapper.find('.control-label');
    if (!field.$wrapper.find('.band-emoji').length) {
      $label.append(`<span class="band-emoji" style="margin-left: 8px; font-size: 1.2em;">${config.emoji}</span>`);
      $label.append(`<span class="band-label" style="margin-left: 8px; font-size: 0.85em; color: ${config.color}; font-weight: 600;">(${config.label})</span>`);
    } else {
      field.$wrapper.find('.band-emoji').text(config.emoji);
      field.$wrapper.find('.band-label').html(`(${config.label})`).css('color', config.color);
    }
  }
}

// Tüm AI Insight alanlarını bir kerede iyileştir
function enhance_ai_insight_fields(frm) {
  setTimeout(() => {
    enhance_sentiment_field(frm);
    enhance_sentiment_trend_field(frm);
    enhance_effort_score_field(frm);
    enhance_effort_band_field(frm);
    
    // AI Summary ve Reply Suggestion alanlarını da güzelleştir
    enhance_text_field(frm, 'ai_summary', '📝', '#e3f2fd');
    enhance_text_field(frm, 'ai_reply_suggestion', '💡', '#fff9e6');
  }, 300);
}

// Text alanlarını iyileştir
function enhance_text_field(frm, fieldname, emoji, bg_color) {
  const field = frm.fields_dict[fieldname];
  if (!field || !field.$wrapper) return;
  
  const $label = field.$wrapper.find('.control-label');
  if (!field.$wrapper.find('.field-emoji').length && $label.length) {
    $label.prepend(`<span class="field-emoji" style="margin-right: 6px; font-size: 1.1em;">${emoji}</span>`);
  }
  
  const $control = field.$wrapper.find('.control-value, .ql-editor, textarea');
  if ($control.length) {
    $control.css({
      'background-color': bg_color,
      'border-radius': '6px',
      'padding': '12px',
      'transition': 'all 0.3s ease'
    });
  }
}

// Yardımcı fonksiyonlar
function get_effort_color(score) {
  // 0-29: Yeşil, 30-69: Sarı-Turuncu, 70-100: Kırmızı
  if (score <= 29) {
    // Yeşil tonları
    const intensity = score / 29;
    return `rgb(${Math.round(40 + intensity * 40)}, ${Math.round(167 - intensity * 20)}, 69)`;
  } else if (score <= 69) {
    // Sarı-turuncu tonları
    const intensity = (score - 30) / 39;
    return `rgb(${Math.round(255)}, ${Math.round(193 - intensity * 50)}, ${Math.round(7)})`;
  } else {
    // Kırmızı tonları
    const intensity = (score - 70) / 30;
    return `rgb(${Math.round(220)}, ${Math.round(53 - intensity * 20)}, ${Math.round(69 - intensity * 30)})`;
  }
}

function get_effort_background(score) {
  // Gradient arka planlar
  if (score <= 29) {
    return 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)';
  } else if (score <= 69) {
    return 'linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%)';
  } else {
    return 'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)';
  }
}

function get_effort_indicator(score) {
  // Görsel gösterge
  if (score <= 29) {
    return '🟢 Mükemmel';
  } else if (score <= 49) {
    return '🟡 İyi';
  } else if (score <= 69) {
    return '🟠 Orta';
  } else if (score <= 89) {
    return '🔴 Yüksek';
  } else {
    return '🔴🔴 Çok Yüksek';
  }
}

// Sidebar alanlarını genişlet
function expand_sidebar_fields(frm) {
  setTimeout(() => {
    // Sidebar içindeki text alanlarını genişlet
    const sidebar_fields = ['ai_summary', 'ai_reply_suggestion'];
    
    sidebar_fields.forEach(fieldname => {
      const field = frm.fields_dict[fieldname];
      if (!field || !field.$wrapper) return;
      
      // Field wrapper'ı bul
      const $field_wrapper = field.$wrapper;
      
      // Text alanını genişlet
      const $control = $field_wrapper.find('.control-value, .ql-editor, textarea, .form-control');
      if ($control.length) {
        $control.css({
          'min-height': '150px',
          'max-height': '400px',
          'overflow-y': 'auto',
          'white-space': 'pre-wrap',
          'word-wrap': 'break-word',
          'line-height': '1.6',
          'padding': '12px',
          'font-size': '13px'
        });
      }
      
      // Label'ı daha belirgin yap
      const $label = $field_wrapper.find('.control-label');
      if ($label.length) {
        $label.css({
          'font-weight': '600',
          'font-size': '13px',
          'margin-bottom': '8px',
          'color': '#4a5568'
        });
      }
      
      // Arka plan rengi ekle (eğer yoksa)
      const bg_colors = {
        'ai_summary': '#f7fafc',
        'ai_reply_suggestion': '#fffaf0'
      };
      
      if (bg_colors[fieldname]) {
        $control.css({
          'background-color': bg_colors[fieldname],
          'border': '1px solid #e2e8f0',
          'border-radius': '6px'
        });
      }
    });
    
    // Sidebar genişliği ve layout ayarlarını KALDIRDIK - orijinal düzen korunuyor
  }, 500);
}

// AI alanlarını badge olarak render et
function render_ai_fields_as_badges(frm) {
  // Last Sentiment
  if (frm.doc.last_sentiment) {
    const sentiment_field = frm.fields_dict.last_sentiment;
    if (sentiment_field && sentiment_field.$wrapper) {
      const html = get_sentiment_badge_html(frm.doc.last_sentiment);
      sentiment_field.$wrapper.find('.control-value').html(html);
    }
  }
  
  // Sentiment Trend
  if (frm.doc.sentiment_trend) {
    const trend_field = frm.fields_dict.sentiment_trend;
    if (trend_field && trend_field.$wrapper) {
      const html = get_sentiment_trend_badge_html(frm.doc.sentiment_trend);
      trend_field.$wrapper.find('.control-value').html(html);
    }
  }
  
  // Effort Score
  if (frm.doc.effort_score !== null && frm.doc.effort_score !== undefined) {
    const score_field = frm.fields_dict.effort_score;
    if (score_field && score_field.$wrapper) {
      const html = get_effort_score_badge_html(frm.doc.effort_score);
      score_field.$wrapper.find('.control-value').html(html);
    }
  }
  
  // Effort Band
  if (frm.doc.effort_band) {
    const band_field = frm.fields_dict.effort_band;
    if (band_field && band_field.$wrapper) {
      const html = get_effort_band_badge_html(frm.doc.effort_band);
      band_field.$wrapper.find('.control-value').html(html);
    }
  }
}

function get_sentiment_badge_html(value) {
  const normalized = value.toLowerCase().trim();
  let emoji, bg, color, label;
  
  if (normalized.includes('olumlu') || normalized.includes('positive')) {
    emoji = '😊';
    bg = '#d4edda';
    color = '#155724';
    label = __('Olumlu');
  } else if (normalized.includes('nötr') || normalized.includes('neutral')) {
    emoji = '😐';
    bg = '#fff3cd';
    color = '#856404';
    label = __('Nötr');
  } else if (normalized.includes('olumsuz') || normalized.includes('negative')) {
    emoji = '😟';
    bg = '#f8d7da';
    color = '#721c24';
    label = __('Olumsuz');
  } else {
    emoji = '❓';
    bg = '#e9ecef';
    color = '#6c757d';
    label = value;
  }
  
  return `<span style="background: ${bg}; color: ${color}; padding: 6px 12px; border-radius: 6px; font-weight: 600; display: inline-block;">
    ${emoji} ${label}
  </span>`;
}

function get_sentiment_trend_badge_html(value) {
  const trend_lower = value.toLowerCase().trim();
  let emoji, bg, color, label;
  
  if (trend_lower.includes('improv') || trend_lower.includes('iyileş') || trend_lower.includes('yüksel')) {
    emoji = '📈';
    bg = '#d4edda';
    color = '#155724';
    label = __('İyileşiyor');
  } else if (trend_lower.includes('declin') || trend_lower.includes('düş') || trend_lower.includes('kötü')) {
    emoji = '📉';
    bg = '#f8d7da';
    color = '#721c24';
    label = __('Kötüleşiyor');
  } else if (trend_lower.includes('stabil') || trend_lower.includes('stable') || trend_lower.includes('sabit')) {
    emoji = '➡️';
    bg = '#cfe2ff';
    color = '#084298';
    label = __('Stabil');
  } else if (trend_lower.includes('volat') || trend_lower.includes('dalgal') || trend_lower.includes('değişken')) {
    emoji = '〰️';
    bg = '#fff3cd';
    color = '#856404';
    label = __('Değişken');
  } else {
    emoji = '📊';
    bg = '#e9ecef';
    color = '#6c757d';
    label = value;
  }
  
  return `<span style="background: ${bg}; color: ${color}; padding: 6px 12px; border-radius: 6px; font-weight: 600; display: inline-block;">
    ${emoji} ${label}
  </span>`;
}

function get_effort_score_badge_html(score) {
  let indicator, bg, color;
  
  if (score <= 29) {
    indicator = '🟢';
    bg = '#d4edda';
    color = '#155724';
  } else if (score <= 49) {
    indicator = '🟡';
    bg = '#fff3cd';
    color = '#856404';
  } else if (score <= 69) {
    indicator = '🟠';
    bg = '#ffe5d0';
    color = '#cc5200';
  } else if (score <= 89) {
    indicator = '🔴';
    bg = '#f8d7da';
    color = '#721c24';
  } else {
    indicator = '🔴🔴';
    bg = '#f8d7da';
    color = '#721c24';
  }
  
  return `<span style="background: ${bg}; color: ${color}; padding: 6px 12px; border-radius: 6px; font-weight: 600; display: inline-block;">
    ${indicator} ${score.toFixed(1)}
  </span>`;
}

function get_effort_band_badge_html(value) {
  const normalized = value.toLowerCase().trim();
  let emoji, bg, color, label;
  
  if (normalized.includes('düşük') || normalized.includes('low')) {
    emoji = '✅';
    bg = '#d4edda';
    color = '#155724';
    label = __('Düşük');
  } else if (normalized.includes('orta') || normalized.includes('medium')) {
    emoji = '⚠️';
    bg = '#fff3cd';
    color = '#856404';
    label = __('Orta');
  } else if (normalized.includes('yüksek') || normalized.includes('high')) {
    emoji = '🔴';
    bg = '#f8d7da';
    color = '#721c24';
    label = __('Yüksek');
  } else {
    emoji = '❓';
    bg = '#e9ecef';
    color = '#6c757d';
    label = value;
  }
  
  return `<span style="background: ${bg}; color: ${color}; padding: 6px 12px; border-radius: 6px; font-weight: 600; display: inline-block;">
    ${emoji} ${label}
  </span>`;
}
