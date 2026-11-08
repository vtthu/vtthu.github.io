from pathlib import Path
import json,sys,shutil,hashlib,zipfile
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import fitz

cfg=json.loads(Path(sys.argv[1]).read_text())
n=cfg['chapter']; title=cfg['title']; count=len(cfg['images'])
# Publish the intact generated artwork on A4 document pages; retain raw images.
raw_images=cfg['images'].copy()
layout_dir=Path('/tmp/comic-batch-585-599')/f'a4-{n}'
layout_dir.mkdir(parents=True,exist_ok=True)
layout_pdf=layout_dir/'layout.pdf'
layout_canvas=canvas.Canvas(str(layout_pdf),pagesize=A4)
for src in raw_images:
    with Image.open(src) as im: w,h=im.size
    scale=min(A4[0]/w,A4[1]/h)
    layout_canvas.drawImage(src,(A4[0]-w*scale)/2,(A4[1]-h*scale)/2,w*scale,h*scale)
    layout_canvas.showPage()
layout_canvas.save()
with fitz.open(layout_pdf) as doc:
    cfg['images']=[]
    for i,page in enumerate(doc,1):
        out=layout_dir/f'trang-{i:02}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.772,1.772),alpha=False).save(out)
        cfg['images'].append(str(out))
cfg['raw_generated_images']=raw_images

root=Path('/workspace/github-comic-backup/pham-nhan-tu-tien')
batch=Path(f'/tmp/comic-batch-585-599/comic-{n}'); dest=root/f'chapters/{n}'
for d in [batch/'pages',batch/'models',dest]:d.mkdir(parents=True,exist_ok=True)
sizes={}
for i,src in enumerate(cfg['images'],1):
    name=f'trang-{i:02}.png'
    with Image.open(src) as im: im.verify()
    with Image.open(src) as im:
        sizes[name]=list(im.size)
        assert abs(im.width/im.height-210/297)<.003,(src,im.size)
    shutil.copy2(src,batch/'pages'/name);shutil.copy2(src,dest/name)
for name in cfg['models']:shutil.copy2(root/'models'/name,batch/'models'/name)
source=Path(f'/workspace/comic-batch-585-599/CHUONG {n}.txt')
shutil.copy2(source,dest/'SOURCE.txt');shutil.copy2(source,batch/'SOURCE.txt')
pdf=batch/f'chuong-{n}.pdf';c=canvas.Canvas(str(pdf),pagesize=A4);c.setTitle(f'Chương {n}: {title}')
for name,(w,h) in sizes.items():
    scale=min(A4[0]/w,A4[1]/h);dw,dh=w*scale,h*scale
    c.drawImage(str(batch/'pages'/name),(A4[0]-dw)/2,(A4[1]-dh)/2,dw,dh);c.showPage()
c.save();shutil.copy2(pdf,dest/pdf.name)
with fitz.open(pdf) as doc:
    assert len(doc)==count
    assert all(abs(p.rect.width-A4[0])<.1 and abs(p.rect.height-A4[1])<.1 for p in doc)
note=f'\n\n## Chương {n} — {title}: hoàn thành {count} trang\nNguồn: file CHUONG {n}.txt do người dùng đính kèm. Mỗi PNG một trang A4 dọc; có thoại, suy nghĩ và lời dẫn. Gắn trực tiếp PNG model gốc tương ứng trong các lần tạo. Bộ chính chapters/{n}/ gồm {count} PNG, PDF A4, SOURCE.txt và README.\n'+cfg['notes']+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name;p.write_text(p.read_text()+note);shutil.copy2(p,batch/name)
readme=f'# Chương {n}: {title}\n\n{count} trang PNG riêng, tỉ lệ A4 dọc; chuyển thể từ văn bản người dùng đính kèm, có thoại, suy nghĩ và lời dẫn. Dùng model tham chiếu trong bộ nhớ dự án.\n\n[PDF A4]({pdf.name}) · [Văn bản nguồn](SOURCE.txt)\n\n'+cfg['summary']+'\n\n'
(dest/'README.md').write_text(readme+'\n'.join(f'![Trang {i}](trang-{i:02}.png)\n' for i in range(1,count+1)))
(batch/'README.md').write_text(readme+'Ảnh ở pages/, model ở models/.\n')
cfg['png_sizes']=sizes;(batch/'MANIFEST.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
hist=root/f'history/comic-{n}';hist.mkdir(parents=True,exist_ok=True)
for name in ['README.md','MANIFEST.json','PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:shutil.copy2(batch/name,hist/name)
rd=root/'README.md';s=rd.read_text();s=s.replace('## Các chương\n',f'## Các chương\n\n- [Chương {n}: {title}](chapters/{n}/): {count} trang, hoàn thành; [PDF A4](chapters/{n}/{pdf.name})\n',1);rd.write_text(s)
mf=root/'ARCHIVE_MANIFEST.json';data=json.loads(mf.read_text())
data['chapters']=[x for x in data['chapters'] if x['chapter']!=n]+[{'chapter':n,'pages':count,'directory':f'chapters/{n}','edition':'user-uploaded-text-adaptation','original_model_reference':True,'pdf':f'chapters/{n}/{pdf.name}','png_sizes':sizes}]
data['files']=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p!=mf]
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
zp=Path(f'/tmp/comic-batch-585-599/truyen-tranh-chuong-{n}.zip')
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(batch.rglob('*')):
        if p.is_file():z.write(p,str(Path(f'chuong-{n}')/p.relative_to(batch)))
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print(json.dumps({'chapter':n,'pages':count,'sizes':sizes,'zip_MB':round(zp.stat().st_size/1e6,1),'pdf_A4_verified':True},ensure_ascii=False))
