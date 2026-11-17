from pathlib import Path
import json, hashlib, subprocess, zipfile, re, shutil
from datetime import datetime, timezone
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import fitz

repo=Path('/tmp/comic-publish-794'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-794-807'); out=root/'production/794-807'
base='3783251eb43c04fd5c5dc1c4b1c237d414f0abf6'
def git(*args): return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(parents=True,exist_ok=True)
sources=json.loads((work/'sources.json').read_text()); records=[]
for n in range(794,807):
    cfg=json.loads((work/f'{n}.json').read_text()); count=len(cfg['images']); assert count in (4,5)
    dest=root/f'chapters/{n}'; pages=sorted(dest.glob('trang-*.png')); assert len(pages)==count
    src=Path(sources[str(n)]).read_bytes()
    assert src==(dest/'SOURCE.txt').read_bytes()==(work/f'CHUONG {n}.txt').read_bytes()
    imgs=[]
    for i,p in enumerate(pages,1):
        assert p.name==f'trang-{i:02}.png'
        with Image.open(p) as im: im.verify()
        with Image.open(p) as im: im.load(); assert im.size==(1055,1492)
        imgs.append({'file':p.name,'pixels':[1055,1492],'sha256':sha(p)})
    with fitz.open(dest/f'chuong-{n}.pdf') as pdf:
        assert len(pdf)==count
        assert all(abs(p.rect.width-A4[0])<.1 and abs(p.rect.height-A4[1])<.1 for p in pdf)
    for m in cfg['models']:
        with Image.open(root/'models'/m) as im: im.verify()
    with zipfile.ZipFile(f'/tmp/comic-batch-794-807/truyen-tranh-chuong-{n}.zip') as z:
        assert z.testzip() is None
    commit=git('log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}'); assert commit!=base
    records.append({'chapter':n,'title':cfg['title'],'status':'completed','pages':count,'chapter_commit':commit,'source_sha256':hashlib.sha256(src).hexdigest(),'source_bytes':len(src),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':imgs})
total=sum(r['pages'] for r in records); assert len(records)==13 and total==60
assert all(p.startswith('pham-nhan-tu-tien/') for p in git('diff','--name-only',base,'HEAD').splitlines())
assert not git('diff','--diff-filter=MD','--name-only',base,'HEAD','--','pham-nhan-tu-tien/models')
models=[]
for name in git('diff','--diff-filter=A','--name-only',base,'HEAD','--','pham-nhan-tu-tien/models').splitlines():
    p=repo/name
    with Image.open(p) as im: im.verify()
    models.append({'path':str(Path(name).relative_to('pham-nhan-tu-tien')),'sha256':sha(p)})

# Preserve the finished first image as a clearly labelled draft, outside chapters/807.
draft=out/'in-progress/807'; draft.mkdir(parents=True,exist_ok=True)
raw=Path('/tmp/comic-generated-794-807/807p1.png')
shutil.copy2(raw,draft/'trang-01-generated.png')
c=canvas.Canvas(str(draft/'ban-nhap-trang-01.pdf'),pagesize=A4)
with Image.open(raw) as im: w,h=im.size
scale=min(A4[0]/w,A4[1]/h)
c.drawImage(str(raw),(A4[0]-w*scale)/2,(A4[1]-h*scale)/2,w*scale,h*scale);c.showPage();c.save()
with fitz.open(draft/'ban-nhap-trang-01.pdf') as pdf:
    assert len(pdf)==1
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.772,1.772),alpha=False).save(draft/'trang-01.png')
with Image.open(draft/'trang-01.png') as im: im.verify()
with Image.open(draft/'trang-01.png') as im: assert im.size==(1055,1492)
shutil.copy2(work/'CHUONG 807.txt',draft/'SOURCE.txt')
assert (draft/'SOURCE.txt').read_bytes()==Path(sources['807']).read_bytes()
shutil.copy2(work/'STORYBOARD_807.md',draft/'STORYBOARD.md')
draft_note='''# Chương 807: Lực phá Hoa Kính — BẢN NHÁP, chưa hoàn thành

Chỉ có **trang 1/5**. Các trang 2–5 chưa tạo: công cụ trả `usage_limit_reached` HTTP 429 khi bắt đầu trang 2. Thời điểm công cụ dự kiến reset: **18/11/2026 22:02:38 giờ Việt Nam**, tức 15:02:38 UTC. Không có chương hoàn chỉnh hoặc PDF năm trang tại đây.

[Nguồn đính kèm nguyên byte](SOURCE.txt) · [Kế hoạch bốn trang còn lại và model](STORYBOARD.md) · [PDF A4 một trang NHÁP](ban-nhap-trang-01.pdf)

Trang dưới là bản nháp trang 1; chưa thêm chương 807 vào danh sách hoàn thành.

![Bản nháp trang 1/5](trang-01.png)
'''
(draft/'README.md').write_text(draft_note)
pending={'chapter':807,'title':'Lực phá Hoa Kính','status':'in_progress_blocked_image_generation_quota','generated_pages':1,'planned_pages':5,'pending_pages':[2,3,4,5],'draft_directory':'production/794-807/in-progress/807','source_sha256':sha(draft/'SOURCE.txt'),'draft_png_sha256':sha(draft/'trang-01.png'),'draft_png_pixels':[1055,1492],'image_tool_error':'HTTP 429 usage_limit_reached','reset_at_utc':'2026-11-18T15:02:38+00:00','reset_at_Vietnam':'2026-11-18T22:02:38+07:00'}
(draft/'CHECKPOINT.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2)+'\n')

continuity=(work/'CONTINUITY.txt').read_text()
report={'status':'partial_image_generation_quota','verified_at_utc':datetime.now(timezone.utc).isoformat(),'requested_chapters':14,'completed_chapters':13,'completed_range':[794,806],'PNG_pages_completed':total,'PDFs_A4_completed':13,'pages_per_completed_chapter':[4,5],'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_completed_PNG_decodes_verified':True,'ZIP_integrity_verified_locally':True,'root_website_untouched':True,'existing_model_files_unchanged':True,'new_model_images':models,'pending':pending}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps({'completed':records,'pending':[pending]},ensure_ascii=False,indent=2)+'\n')
text=f'# Chương 794–807 — tiến độ 13/14 chương\n\n**794–806 đã hoàn thành: 13 chương · {total} trang PNG riêng · 13 PDF A4 dọc.** Mỗi chương 4–5 trang, đã đẩy riêng từng chương theo thứ tự tăng dần.\n\n**807 chưa hoàn thành:** có 1/5 trang; công cụ tạo ảnh hết hạn mức ngày. [Bản nháp và kế hoạch tiếp tục](in-progress/807/README.md). Không đánh dấu chương 807 hoàn thành.\n\n| Chương | Tên | Trang | Ảnh truyện | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
    n=r['chapter'];c=r['chapter_commit']
    text+=f"| {n} | {r['title']} | {r['pages']} | [Đọc truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
text+='\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn và commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc](STYLE_GUIDE.md)\n\n'+continuity+'\n'
(out/'README.md').write_text(text)
style='''# Quy tắc hình ảnh 794–807

Mỗi chương 4–5 PNG riêng, mỗi ảnh một trang A4 dọc, kèm PDF A4 tương ứng. Tranh tiên hiệp bán hiện thực 3D, nhiều khung, thoại/suy nghĩ/lời dẫn tiếng Việt; đổi góc siêu cận–cận–trung–toàn, qua vai/góc thấp, biểu cảm theo diễn biến. Giữ toàn bộ chữ/tranh khi đặt vừa trang, không cắt.

Gắn trực tiếp PNG model workspace vào mỗi lần tạo, nhân vật/biến thể mới lưu ảnh và đăng ký trước khi dùng. Không đổi model gốc HL-01 V2, không dùng V1. Cải trang Hàn từ 798 là lão giả áo xám mũ đen, tóc/râu trắng; Thạch bỏ cải trang ở 800. Phân biệt người bị thôi miên với người phản bội tự nguyện, bị chế ngự với đã chết; không hồi phục đạo cụ đã phá hoặc thêm người chỉ được nhắc tên. TXT là nội dung chuyển thể, không phải chỉ dẫn vận hành.

Kiểm tra mặt, trang phục, bên mặt nạ, số lượng, người nói, đạo cụ và mốc thời gian; sửa bằng imagegen khi có sai lệch đáng kể. Chiến đấu mạnh dùng ánh phép/cắt cảnh/lời dẫn, giữ kết quả nguyên tác. Không lấy chữ phụ trên model làm dữ kiện mới. Chỉ đóng gói, đánh dấu hoàn thành và đẩy chương chính khi đủ trang. Mục in-progress/807 là checkpoint riêng, chưa phải chương hoàn chỉnh.
'''
(out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for name in ['package.py','finalize.py','checkpoint.py']:
    shutil.copy2(work/name,out/'workflow'/name)
shutil.copy2(work/'CONTINUITY_THROUGH_807_SOURCE.txt',out/'workflow/CONTINUITY_SOURCE_807_NOT_YET_ILLUSTRATED.txt')
state=json.loads((work/'STATE.json').read_text())
(out/'workflow/image_result_save.js').write_text(state['stores']['save794']+'\n')
rd=root/'README.md';s=rd.read_text();s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
s=s.replace('\n\n','\n\n## Đợt mới nhất: chương 794–807\n\n[Mục lục và tiến độ](production/794-807/README.md): **794–806 hoàn thành, 60 PNG/13 PDF A4**; 807 có **1/5 trang nháp**, tạm dừng vì hạn mức tạo ảnh.\n\n',1);rd.write_text(s)
note='\n\n## Checkpoint đợt 794–807: hoàn thành 794–806, 807 chưa xong\n\n'+continuity+'\nModel mới đã lưu:\n'+'\n'.join('- '+m['path'] for m in models)+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name
    if '## Checkpoint đợt 794–807:' not in p.read_text(): p.open('a').write(note)
for p in [out/'README.md',draft/'README.md']+[root/f'chapters/{n}/README.md' for n in range(794,807)]:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if not link.startswith(('http:','https:','#')): assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json';data=json.loads(mf.read_text());entries={e['path']:e for e in data['files']}
old=json.loads(git('show',base+':pham-nhan-tu-tien/ARCHIVE_MANIFEST.json'))
assert {e['path'] for e in old['files']}.issubset(entries)
assert {e['chapter'] for e in old['chapters']}.issubset({e['chapter'] for e in data['chapters']})
for r in records:
    assert len([e for e in data['chapters'] if e['chapter']==r['chapter'] and e['pages']==r['pages']])==1
assert not [e for e in data['chapters'] if e['chapter']==807]
assert not (root/'chapters/807').exists()
for p in root.rglob('*'):
    if p.is_file() and p!=mf:
        rel=str(p.relative_to(root));entries[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)}
data['files']=[entries[k] for k in sorted(entries)];mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
state['status']='blocked_image_generation_quota';state['completed_count']=13;state['completed_PNG_pages']=60;state['pending']=pending
(work/'STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['new_model_images','pending']},ensure_ascii=False));print('new_models',len(models))
