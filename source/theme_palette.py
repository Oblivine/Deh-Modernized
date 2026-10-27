import colorsys,re

def theme_palette(markup):
    mapping={}
    def color_token(m):
        value=m.group(0).lower();h=value[1:]
        if len(h) in (3,4):h=''.join(c*2 for c in h)
        if len(h) not in (6,8):return value
        r,g,b=[int(h[i:i+2],16) for i in (0,2,4)]
        if not (r>=g>=b and r-b>=5):return value
        key='--tone-'+h
        _,light,saturation=colorsys.rgb_to_hls(r/255,g/255,b/255)
        cyan=colorsys.hls_to_rgb(.5,light,saturation)
        out='#'+''.join(f'{round(v*255):02x}' for v in cyan)+h[6:]
        mapping[key]=(value,out)
        return 'var('+key+')'
    def block(m):
        css=re.sub(r'#[0-9a-fA-F]{3,8}(?![0-9a-fA-F-])',color_token,m.group(1))
        return '<style>'+css+'</style>'
    result=re.sub(r'<style>(.*?)</style>',block,markup,flags=re.S)
    amber=';'.join(k+':'+v[0] for k,v in sorted(mapping.items()))
    cyan=';'.join(k+':'+v[1] for k,v in sorted(mapping.items()))
    style='<style>#x3-2008{'+amber+'}#x3-2008[data-illumination="cyan"]{'+cyan+';--amber:#00ffff;--hot:#d3ffff;--mid:#83d9de;--dim:#589ca2;--off:#1d3e42}#x3-2008{--bg:#000}#x3-2008 .ax-lcd,#x3-2008 #ax-main{background:#000!important}#x3-2008 .mx-color-preview{height:145px;aspect-ratio:auto;margin:14px 0 0}#x3-2008 .mx-display-tabs{display:flex;gap:7px;margin-bottom:12px}#x3-2008 .mx-display-tabs button{flex:1;min-height:42px}#x3-2008 .mx-color-note{font-size:12px;line-height:1.5;color:var(--mid);margin:10px 0}@media(max-width:480px){#x3-2008 .mx-color-preview{height:100px}}</style>'
    return result.replace('<script id="x3-original-assets"',style+'\n<script id="x3-original-assets"')
