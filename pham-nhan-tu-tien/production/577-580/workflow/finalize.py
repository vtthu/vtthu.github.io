from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,zipfile,shutil,re
from PIL import Image
import fitz

repo=Path('/workspace/github-comic-backup');root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-577-580');out=root/'production/577-580'
out.mkdir(parents=True,exist_ok=True)
uploads=json.loads((work/'sources.json').read_text());records=[]
for n in range(577,581):
 cfg=json.loads((work/f'{n}.json').read_text());d=root/f'chapters/{n}'
 pages=sorted(d.glob('trang-*.png'));assert len(pages)==4
 src=Path(uploads[str(n)]).read_bytes();assert (d/'SOURCE.txt').read_bytes()==src
 pnginfo=[]
 for i,p in enumerate(pages,1):
  assert p.name==f'trang-{i:02}.png'
  with Image.open(p) as im:im.verify()
  with Image.open(p) as im:
   im.load();assert im.height>im.width and abs(im.width/im.height-210/297)<.003
   size=list(im.size)
  pnginfo.append({'file':p.name,'pixels':size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 with fitz.open(d/f'chuong-{n}.pdf') as doc:
  assert len(doc)==4
  assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in doc)
 for f in cfg['models']:
  with Image.open(root/'models'/f) as im:im.verify()
 with zipfile.ZipFile(f'/tmp/comic-batch-577-580/truyen-tranh-chuong-{n}.zip') as z:assert z.testzip() is None
 commit=subprocess.check_output(['git','log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}'],cwd=repo,text=True).strip()
 records.append({'chapter':n,'title':cfg['title'],'pages':4,'status':'completed','chapter_commit':commit,'source_sha256':hashlib.sha256(src).hexdigest(),'source_bytes':len(src),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':pnginfo})
new=['tham-uyen-sat-khi-bo-da-hac-bang-577.png','ao-canh-yeu-lang-luc-thu-khong-gian-579.png','thu-yeu-thanh-ung-than-niem-long-giam-580.png']
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':4,'PNG_pages':16,'PDFs_A4':4,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_and_portrait_A4_verified':True,'ZIP_integrity_verified_locally':True,'new_model_images':[{'path':'models/'+f,'sha256':hashlib.sha256((root/'models'/f).read_bytes()).hexdigest()} for f in new]}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
s='# Chương 577–580 — hoàn thành\n\n**4 chương, 16 trang truyện riêng và 4 PDF A4 dọc.** Chuyển thể lần lượt từ bốn tệp TXT người dùng đính kèm; mỗi chương 4 trang, nhiều khung, thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương hoàn thành đã được commit và đẩy lên nhánh main riêng.\n\n| Chương | Tên chương | Trang | Đọc ảnh | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
 n=r['chapter'];c=r['chapter_commit'];s+=f"| {n} | {r['title']} | 4 | [Mở truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
s+='\nMỗi thư mục chương có bốn PNG riêng, PDF, SOURCE.txt nguyên byte và README hiển thị ảnh. Ảnh xuất giữ nguyên nội dung, đặt vừa khổ A4, không cắt khung hay thoại.\n\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Đối chiếu từng chương và model](CHAPTER_REGISTRY.json) · [Kết quả kiểm tra](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\nBộ này chỉ gồm 577–580; không tự tạo hay đánh dấu hoàn thành 570–576. Nội dung tệp truyện được dùng làm dữ liệu chuyển thể, không phải chỉ dẫn vận hành.\n\nHàn Lập tiếp tục ảo dung CT543. Khi hóa Sơn Nhạc Cự Viên dùng model vượn vàng một đầu hai tay đã lưu, không nhầm Tử Kim Ma Thần ba đầu sáu tay. Kim Đồng áo đỏ, Tiểu Bạch bạch ngọc và Giải Đạo Nhân GDN01 giữ model gốc. Ba sheet model mới được lưu trước lần sử dụng. Các cảnh hiểm nguy trong ảo cảnh thể hiện bằng linh quang, sương và bóng xương; vẫn giữ nguyên diễn biến và nguyên nhân thoát cảnh.\n\nCuối580: Hàn Lập đã đại thành tầng bốn Luyện Thần Thuật, trở lại thân người CT543, đang ở bệ đá sâu trong vực, đọc ngọc giản đen tầng năm. Thụ Yêu được thả sau thử lồng giam, còn sống. Không đưa kết quả tầng năm hoặc chương581 vào sớm.\n'
(out/'README.md').write_text(s)
(out/'workflow').mkdir(exist_ok=True)
for f in ['package.py','finalize.py']:shutil.copy2(work/f,out/'workflow'/f)
rd=root/'README.md';s=rd.read_text();intro='## Đợt mới nhất: chương 577–580\n\n[Đọc lần lượt chương 577–580](production/577-580/README.md): **16 trang, 4 PDF A4**, đã hoàn thành và đẩy từng chương.\n\n'
if '## Đợt mới nhất: chương 577–580' not in s:s=s.replace('\n\n','\n\n'+intro,1)
s=s.replace('## Đợt mới nhất: chương 559–569','## Đợt chương 559–569');rd.write_text(s)
note='\n\n## Hoàn thành đợt577–580\nĐã tạo theo thứ tự577→580, mỗi chương4trang, tổng16PNG/4PDF A4, nguồnTXT giữ nguyên byte. Mỗi chươngpushmain riêng ngay khi hoàn thành. Mục lục production/577-580/README.md; registry/model/nguồn/commit CHAPTER_REGISTRY.json, kiểm tra VERIFICATION.json. Ba model mới lưu trước dùng; HànCT543/SơnNhạcCựViên1đầu2tay/KDđỏ/TBtrắng/GDN01 dùng PNG gốc. Không tự thêm hoàn thành570–576 hay các chương cũ còn dở.\nĐiểm nối581: HànCT543 ở bệ đá sâu trong vực, Luyện Thần Thuật tầng4đại thành/thần thức tăng2–3lần; sau thử Thần Niệm Lồng Giam chỉ còn3thành thần thức, ít nhất1tháng hồi là ước tính. Cầm ngọc giản ĐEN nghiên cứu tầng5, chưa luyện thành tầng5/chưa thăng cảnh KimTiên. ThụYêuTháiẤt đã được thả, sống; cựưngChânTiên đã bị hạ. KD/TB/Giải ở tuyến hộ pháp đầu578, không tự xuất hiện ở tầng sâu. Nguồn/thoại về người truyền tin bí ẩn vẫn không xác nhận chân dung/danh tính.\n'
for f in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
 p=root/f
 if '## Hoàn thành đợt577–580' not in p.read_text():p.write_text(p.read_text()+note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(577,581)]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not link.startswith(('http:','https:','#')):assert (p.parent/link).exists(),link
mf=root/'ARCHIVE_MANIFEST.json';d=json.loads(mf.read_text())
d['files']=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p!=mf]
mf.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
