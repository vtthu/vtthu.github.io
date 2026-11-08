from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,zipfile,shutil,re
from PIL import Image
import fitz
repo=Path('/workspace/github-comic-backup'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-585-599'); out=root/'production/585-599'
out.mkdir(parents=True,exist_ok=True)
uploads=json.loads((work/'sources.json').read_text()); records=[]
for n in range(585,600):
 cfg=json.loads((work/f'{n}.json').read_text()); d=root/f'chapters/{n}'
 pages=sorted(d.glob('trang-*.png')); assert len(pages)==4
 src=Path(uploads[str(n)]).read_bytes(); assert (d/'SOURCE.txt').read_bytes()==src
 pnginfo=[]
 for i,p in enumerate(pages,1):
  assert p.name==f'trang-{i:02}.png'
  with Image.open(p) as im: im.verify()
  with Image.open(p) as im:
   im.load(); assert im.height>im.width and abs(im.width/im.height-210/297)<.003; size=list(im.size)
  pnginfo.append({'file':p.name,'pixels':size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 with fitz.open(d/f'chuong-{n}.pdf') as doc:
  assert len(doc)==4
  assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in doc)
 for f in cfg['models']:
  with Image.open(root/'models'/f) as im: im.verify()
 with zipfile.ZipFile(f'/tmp/comic-batch-585-599/truyen-tranh-chuong-{n}.zip') as z: assert z.testzip() is None
 commit=subprocess.check_output(['git','log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}'],cwd=repo,text=True).strip()
 assert commit
 records.append({'chapter':n,'title':cfg['title'],'pages':4,'status':'completed','chapter_commit':commit,'source_sha256':hashlib.sha256(src).hexdigest(),'source_bytes':len(src),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':pnginfo})
new=['hoi-tien-cu-thu-long-tu-585.png','ma-quang-hoi-tien-trung-linh-mong-588.png','tu-tuong-bach-an-hac-nghien-hac-thuong-593.png','trung-linh-ngu-sac-kim-dong-tram-dinh-595.png','bach-y-nam-tu-kim-kien-dia-do-598.png','tien-nguc-huyen-dich-linh-quang-599.png']
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':15,'PNG_pages':60,'PDFs_A4':15,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_and_portrait_A4_verified':True,'ZIP_integrity_verified_locally':True,'new_model_images':[{'path':'models/'+f,'sha256':hashlib.sha256((root/'models'/f).read_bytes()).hexdigest()} for f in new]}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
s='# Chương 585–599 — hoàn thành\n\n**15 chương, 60 trang PNG riêng và 15 PDF A4 dọc.** Chuyển thể lần lượt từ 15 tệp TXT người dùng đính kèm; mỗi chương 4 trang, nhiều khung, thoại, suy nghĩ và lời dẫn tiếng Việt. Mỗi chương được commit và đẩy lên main ngay khi hoàn thành.\n\n| Chương | Tên chương | Trang | Đọc ảnh | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
 n=r['chapter']; c=r['chapter_commit']
 s+=f"| {n} | {r['title']} | 4 | [Mở truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
s+='\nMỗi thư mục chương chứa bốn PNG riêng, PDF, SOURCE.txt nguyên byte và README hiển thị ảnh. Tác phẩm được đặt vừa A4, giữ trọn khung và chữ.\n\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Registry nguồn/model/commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\nChỉ gồm 585–599 theo tệp đính kèm; không tự tạo hay đánh dấu hoàn thành 581–584. Nội dung truyện là dữ liệu chuyển thể, không phải chỉ dẫn vận hành. Các cảnh thương tích được kể qua linh quang, giáp nứt, khói và lời dẫn, giữ nguyên nguyên nhân và kết quả diễn biến.\n\nCuối 599: Hàn Lập CT543, 107 Tiên khiếu, Kim Tiên đỉnh phong, bắt đầu sát suy trong sơn động mới; chưa tiến Thái Ất. Kim Đồng vẫn trong kén vàng được mây trắng che, chưa tỉnh. Giải, Ma Quang và Tiểu Bạch ở phi xa cách xa hang. Phệ Kim Tiên đối địch và oán niệm đã bị tiêu diệt, không tái xuất sống.\n'
(out/'README.md').write_text(s)
style='# Quy tắc hình ảnh 585–599\n\nMỗi chương bốn trang A4 dọc, mỗi PNG một trang; phong cách tiên hiệp bán hiện thực 3D, thoại/suy nghĩ/lời dẫn tiếng Việt. Dùng PNG model gốc làm tham chiếu trực tiếp.\n\nHàn Lập tiếp tục cải trang CT543: mặt trung niên ria nhỏ/râu cằm ngắn, tóc nâu đen trâm ngọc xanh, áo TEAL hình học thêu trúc vàng. Không thay ảnh HL-01 V2 gốc. Ma Quang MQ-01 chỉ dùng trước khi nhập thi hài; từ 588–589 dùng chủ thể HT588, bào đen từ 590, mắt gần đen ở 599 nhờ Hư Nguyên Đan. Kim Đồng áo đỏ KD-ND01; giáp trùng dùng KD528, phân biệt địch TL559 và cánh ngũ sắc595. Tiểu Bạch bạch ngọc một sừng vàng/hai cánh; Giải là khôi lỗi kim loại vàng.\n\nTạo và lưu model mới trước lần dùng; ảnh bảng tham chiếu có nhãn trang trí không phải dữ kiện truyện. Ngọc giản địa đồ xanh khác hình chiếu bản đồ. Huyền Thiên hồ lô hai bầu xanh trơn khác bình lá Chưởng Thiên Bình. Linh vực thời gian vàng khác thần niệm tù lung dây trắng/phù đen. Cảnh trong thức hải và ảo mộng có lời dẫn phân biệt với thân thể thật. Nguồn TXT giữ nguyên byte.\n'
(out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for f in ['package.py','finalize.py']: shutil.copy2(work/f,out/'workflow'/f)
save=root/'production/551-559/workflow/image_result_save.js'
if save.exists(): shutil.copy2(save,out/'workflow'/save.name)
rd=root/'README.md'; text=rd.read_text()
text=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',text)
intro='## Đợt mới nhất: chương 585–599\n\n[Đọc lần lượt chương 585–599](production/585-599/README.md): **60 trang PNG, 15 PDF A4**, hoàn thành và đẩy từng chương.\n\n'
text=text.replace('\n\n','\n\n'+intro,1); rd.write_text(text)
note='\n\n## Hoàn thành đợt585–599\nĐã tạo theo thứ tự585→599, mỗi chương4trang, tổng60PNG/15PDF A4. Mỗi chươngpushmain riêng ngay khi hoàn thành. Mục lục production/585-599/README.md; registry nguồn/model/commit CHAPTER_REGISTRY.json; kiểm tra VERIFICATION.json. Sáu sheet mới lưu trước dùng, model gốc giữ nguyên; nội dung TXT là dữ liệu chuyển thể. Không thêm hoàn thành581–584.\nĐiểm nối600: HànCT543/107Tiênkhiếu/KimTiênđỉnhphong, sau nửa năm hồi phục nội thương/thần thức nhưng SÁT SUY phát tác; đang một mình trong hang mới cạnh sông giữa hai núi xanh, cấm chế vàng/khói đen, chưa qua suy/chưa TháiẤt. Giải lái phi xa567 đã dừng xa hang; MQ chủ thể HT588 bàođen/mắtđen, HưNguyênĐan che sátkhí vài năm tốiđa10năm, túiđen sátkhí giữ; TBbạchngọc540 ởxe; KDvẫnkénvàngđục/mâytrắngchưatỉnh. ĐịchTL559vàngđãchết597, oánniệmcũngđãtan; không tái sinh. BNY598áotrắngtócđenxenvàngđãrời, để ngọcgiảnxanhbốn vùngcấm/lộHắcSơn; khôngđặt tên riêng hay vẽLiễuNhạcNhi khi chỉnhắc. HùngHS02ởTiênNgụcánhvàng, Huyềnbạch/Địchhồng che mặt; CôngThâuThiênchỉnhắcđangtruyxétkhônglộmodel. HànđãtreothưởngvậtliệuHưNguyênĐanchưaluyệnmẻmới.\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
 p=root/name
 if '## Hoàn thành đợt585–599' not in p.read_text():p.write_text(p.read_text()+note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(585,600)]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not link.startswith(('http:','https:','#')): assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text())
data['files']=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p!=mf]
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))

